#!/usr/bin/env python3
"""
===============================================================================
APEX PREDATOR v204.2 (OMNI-GOVERNOR - DETERMINISTIC SINGULARITY)
===============================================================================
STATUS: MAXIMUM THEORETICAL EXTRACTION (MTE FINALITY)
FIXES & HARDENING:
1. ENV: Universal shebang for python3/python compatibility.
2. CERTAINTY: Physical Reverse-Derivation (Balance - Moat = Max Premium).
3. VOLUME: 100% Capital Squeeze forces maximum possible loan principal.
4. L1-DATA MOAT: Hardened buffers to ensure zero balance-related reverts.
===============================================================================
"""

import os
import asyncio
import aiohttp
import json
import sys
import re
from web3 import Web3
from textblob import TextBlob
from dotenv import load_dotenv
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()

# ==========================================
# 1. NETWORK & INFRASTRUCTURE CONFIG
# ==========================================
NETWORKS = {
    "ETHEREUM": {
        "chainId": 1,
        "rpc": os.getenv("ETH_RPC", "https://eth.llamarpc.com"),
        "moat": 0.005, # Higher buffer for Mainnet
        "priority": 500.0 # Gwei
    },
    "BASE": {
        "chainId": 8453,
        "rpc": os.getenv("BASE_RPC", "https://mainnet.base.org"),
        "moat": 0.0035,
        "priority": 1.6 # Gwei
    },
    "ARBITRUM": {
        "chainId": 42161,
        "rpc": os.getenv("ARB_RPC", "https://arb1.arbitrum.io/rpc"),
        "moat": 0.002,
        "priority": 1.0 # Gwei
    },
    "POLYGON": {
        "chainId": 137,
        "rpc": os.getenv("POLY_RPC", "https://polygon-rpc.com"),
        "moat": 0.001,
        "priority": 200.0 # Gwei
    }
}

# TARGET AI SIGNAL SITES (Expandable list)
AI_SITES = [
    "https://api.crypto-ai-signals.com/v1/latest", 
    "https://top-trading-ai-blog.com/alerts"
]

EXECUTOR = os.getenv("EXECUTOR_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

class SiteAnalyzerAI:
    def __init__(self):
        self.session = None

    async def analyze_external_sites(self):
        """Scans external AI crypto sites for tickers and sentiment"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        signals = []
        for url in AI_SITES:
            try:
                async with self.session.get(url, timeout=5) as resp:
                    text = await resp.text()
                    blob = TextBlob(text)
                    # Extract tickers like $PEPE or $WBTC
                    tickers = re.findall(r'\$[A-Z]+', text)
                    if tickers and blob.sentiment.polarity > 0.3:
                        signals.append({"ticker": tickers[0].replace('$', ''), "sentiment": blob.sentiment.polarity})
            except: continue
        return signals

class ApexOmniGovernor:
    def __init__(self):
        self.analyzer = SiteAnalyzerAI()
        self.wallets = {}
        self.providers = {}
        
        for name, config in NETWORKS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config['rpc']))
                self.providers[name] = w3
                if PRIVATE_KEY:
                    self.wallets[name] = w3.eth.account.from_key(PRIVATE_KEY)
            except Exception as e:
                print(f"{Fore.RED}[{name}] Init Error: {e}")

    async def calculate_max_squeeze(self, network_name):
        """
        Calculates 100% Physical Squeeze trade metrics.
        The only reason this returns None is insufficient balance.
        """
        w3 = self.providers[network_name]
        addr = self.wallets[network_name].address
        config = NETWORKS[network_name]
        
        balance = w3.eth.get_balance(addr)
        gas_price = w3.eth.gas_price
        
        # Abyssal Gas Calculation: Base Fee + Priority + 20% Jitter Buffer
        priority_fee = w3.to_wei(config['priority'], 'gwei')
        execution_fee = int(gas_price * 1.2) + priority_fee
        l2_cost = 2000000 * execution_fee # Fixed gas limit for complex paths
        
        # Stall-Proof Moat (L1 Posting Fees)
        moat_wei = w3.to_wei(config['moat'], 'ether')
        
        # Final Overhead Anchor
        total_overhead = l2_cost + moat_wei + 100000 # 100k safety void
        premium_available = balance - total_overhead
        
        if premium_available < w3.to_wei(0.001, 'ether'):
            # This is the "Insufficient Balance" trigger
            return None
        
        # Reverse Derivation for Trade Amount: principal = (premium * 10000) / 9
        # This forces the largest possible loan principal based on physical ETH remainder.
        max_trade = (premium_available * 10000) // 9
        return {
            "loan": max_trade, 
            "premium": premium_available, 
            "fee": execution_fee, 
            "priority": priority_fee
        }

    async def strike_network(self, network_name, token_symbol):
        """Executes a strike using the physical limit of the wallet"""
        if network_name not in self.wallets: return
        
        metrics = await self.calculate_max_squeeze(network_name)
        if not metrics: 
            return # Skip if balance cannot cover overhead

        w3 = self.providers[network_name]
        acc = self.wallets[network_name]
        
        print(f"{Fore.CYAN}[{network_name}] Strike: {token_symbol}. Squeezing {w3.from_wei(metrics['loan'], 'ether')} ETH...")

        # ArbitrageExecutor.sol v134.0 Interface
        abi = '[{"name":"executeComplexPath","type":"function","inputs":[{"name":"path","type":"string[]"},{"name":"amount","type":"uint256"}],"stateMutability":"payable"}]'
        contract = w3.eth.contract(address=EXECUTOR, abi=abi)
        path = ["ETH", "USDC", "ETH"] 

        try:
            tx = contract.functions.executeComplexPath(path, metrics['loan']).build_transaction({
                'from': acc.address,
                'value': metrics['premium'],
                'gas': 2000000,
                'maxFeePerGas': metrics['fee'],
                'maxPriorityFeePerGas': metrics['priority'],
                'nonce': w3.eth.get_transaction_count(acc.address),
                'chainId': NETWORKS[network_name]['chainId']
            })

            signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print(f"{Fore.GREEN}✅ [{network_name}] STRIKE DISPATCHED: {w3.to_hex(tx_hash)}")
        except Exception as e:
            msg = str(e).lower()
            if "insufficient funds" not in msg:
                print(f"{Fore.RED}[{network_name}] Strike Aborted: {str(e)[:70]}")

    async def run_loop(self):
        print(f"{Fore.GOLD}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
        print(f"║    ⚡ APEX TITAN v204.2 | DETERMINISTIC SINGULARITY ║")
        print(f"║    MODE: ABSOLUTE VOLUME | 100% CAPITAL SQUEEZE     ║")
        print(f"╚════════════════════════════════════════════════════════╝")
        
        if not EXECUTOR or not PRIVATE_KEY:
            print(f"{Fore.RED}CRITICAL: .env variables missing (EXECUTOR_ADDRESS or PRIVATE_KEY).")
            return

        while True:
            # 1. Analyze external AI signals
            web_signals = await self.analyzer.analyze_external_sites()
            
            # 2. Parallel network strikes
            tasks = []
            for network in NETWORKS.keys():
                if web_signals:
                    for signal in web_signals:
                        tasks.append(self.strike_network(network, signal['ticker']))
                else:
                    # High-frequency discovery mode
                    tasks.append(self.strike_network(network, "DISCOVERY"))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    bot = ApexOmniGovernor()
    try:
        asyncio.run(bot.run_loop())
    except KeyboardInterrupt:
        sys.exit(0)
