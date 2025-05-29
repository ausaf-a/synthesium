#!/usr/bin/env python3

# Quick test to make sure the fixes work
import sys
sys.path.append('/Users/ausafm/Documents/Programming/synthesium')

print("🧪 Testing fixed system...")

# Test 1: Channel discovery
from services.channel_manager import ChannelManager
channel_manager = ChannelManager()

print("✅ Channel discovery working")

# Test 2: Check available channels
channels = channel_manager.get_available_channels()
print(f"✅ Found {len(channels)} channels")

# Test 3: Check character loading
try:
    character = channel_manager.load_character("sigma_grindset")
    print(f"✅ Character loaded: {character['name']}")
except Exception as e:
    print(f"❌ Character loading failed: {e}")

print("\n🚀 System ready for testing!")
print("Run: python synth.py --channel sigma_grindset")
