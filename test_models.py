#!/usr/bin/env python3
"""
Test script to check available models from z.ai API
"""

from openai import OpenAI

# Configure client
client = OpenAI(
    api_key="bfc0ba4defa24b909bae2fdce3f7802e.cia5P6s2JimydvkQ",
    base_url="https://api.z.ai/api/coding/paas/v4"
)

print("Testing different model names...\n")

# Test models to try
test_models = [
    "glm-4",
    "glm-4-air",
    "GLM-4",
    "GLM-4-Air",
    "glm-4-plus",
    "glm-4-0520",
    "glm-4-airx",
    "glm-4-flash"
]

for model in test_models:
    try:
        print(f"Testing model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Hi"}
            ],
            max_tokens=10
        )
        print(f"  ✅ SUCCESS! Model {model} works!")
        print(f"  Response: {response.choices[0].message.content}\n")
        break
    except Exception as e:
        error_msg = str(e)
        if "1211" in error_msg:
            print(f"  ❌ Model not found\n")
        else:
            print(f"  ❌ Error: {error_msg}\n")

