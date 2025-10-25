#!/usr/bin/env python3
"""
Quick test for glm-4.6 model name
"""

from openai import OpenAI

client = OpenAI(
    api_key="bfc0ba4defa24b909bae2fdce3f7802e.cia5P6s2JimydvkQ",
    base_url="https://api.z.ai/api/coding/paas/v4"
)

print("Testing glm-4.6 model...\n")

try:
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[
            {"role": "user", "content": "Say hello in one sentence"}
        ],
        max_tokens=50
    )
    print(f"✅ SUCCESS! Model 'glm-4.6' works!")
    print(f"Response: {response.choices[0].message.content}\n")
except Exception as e:
    print(f"❌ Error: {str(e)}\n")
    
    # Try alternative names
    print("Trying alternative names...")
    for model in ["GLM-4.6", "glm-4-6", "GLM-4-6", "glm4.6", "GLM4.6"]:
        try:
            print(f"  Testing: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            print(f"  ✅ SUCCESS with {model}!")
            print(f"  Response: {response.choices[0].message.content}\n")
            break
        except Exception as e2:
            error_msg = str(e2)
            if "1211" in error_msg:
                print(f"  ❌ Not found")
            elif "1113" in error_msg:
                print(f"  ⚠️ Found but insufficient balance")
                break
            else:
                print(f"  ❌ Error: {error_msg[:50]}")

