import subprocess

print("🎛️  Choose image sharing method:")
print("1. MA (Modular arithmetic)")
print("2. XOR (Bitwise XOR)")
print("3. BLD (Bitleveldecompositionlevel)")

method = input("Enter method (MA / XOR / BLD): ").strip().upper()

if method == "MA":
    print("\n🚀 Running Modular Arithmetic channel...")
    subprocess.run(["python", "server.py"])
    subprocess.run(["python", "client2.py"])
    subprocess.run(["python", "client3.py"])

elif method == "XOR":
    print("\n🚀 Running XOR channel...")
    subprocess.run(["python", "serverxor.py"])
    subprocess.run(["python", "client2xor.py"])
    subprocess.run(["python", "client3xor.py"])

elif method == "BLD":
    print("\n🚀 Running Bitleveldecomposition channel...")
    subprocess.run(["python", "serverbld.py"])
    subprocess.run(["python", "client2bld.py"])
    subprocess.run(["python", "client3bld.py"])

else:
    print("❌ Invalid method selected. Please choose MA, XOR, or BLD.")

