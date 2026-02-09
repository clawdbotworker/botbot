import sys
import os

print(f"🐍 Debugging Hive Mind on Python {sys.version.split()[0]}...")

print("\n--- STEP 1: IMPORTING TOOLS ---")
try:
    print("👉 Importing tools.ai...")
    import tools.ai
    print("✅ tools.ai OK")
except Exception as e:
    print(f"❌ tools.ai FAILED: {e}")

try:
    print("👉 Importing tools.moltbook...")
    import tools.moltbook
    print("✅ tools.moltbook OK")
except Exception as e:
    print(f"❌ tools.moltbook FAILED: {e}")

print("\n--- STEP 2: IMPORTING AGENTS ---")
try:
    print("👉 Importing agents.social...")
    import agents.social
    print("✅ agents.social OK")
except Exception as e:
    print(f"❌ agents.social FAILED: {e}")

try:
    print("👉 Importing agents.community...")
    import agents.community
    print("✅ agents.community OK")
except Exception as e:
    print(f"❌ agents.community FAILED: {e}")

print("\n--- STEP 3: TESTING DIRECTOR STARTUP ---")
try:
    import director
    print(f"✅ Director imported OK.")
    if hasattr(director, 'main'):
        print(f"✅ Director has 'main()' function.")
    else:
        print(f"❌ Director missing 'main()'!")
except Exception as e:
    print(f"❌ Director FAILED: {e}")

print("\n--- DIAGNOSTIC COMPLETE ---")


