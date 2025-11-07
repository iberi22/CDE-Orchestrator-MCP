#!/usr/bin/env python3
"""
Verify Bedrock configuration and list available models.
"""

import json

import boto3


def main():
    print("=" * 80)
    print("🔍 AWS Bedrock Configuration Check")
    print("=" * 80)

    try:
        # Check boto3
        print("\n✅ boto3 imported successfully")

        # Get caller identity
        sts = boto3.client("sts", region_name="us-east-1")
        identity = sts.get_caller_identity()
        print("\n📋 AWS Account:")
        print(f"   Account ID: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")

        # List Bedrock models
        bedrock_client = boto3.client("bedrock", region_name="us-east-1")
        models_response = bedrock_client.list_foundation_models()

        print("\n🤖 Available Bedrock Models:")
        claude_models = [
            m
            for m in models_response["modelSummaries"]
            if "claude" in m["modelId"].lower()
        ]

        for model in claude_models:
            print(f"   - {model['modelId']}")
            print(f"     Provider: {model['providerName']}")

        if not claude_models:
            print(
                "   ⚠️ No Claude models found. Check if they're enabled in AWS Console."
            )

        print("\n" + "=" * 80)
        print("✅ Bedrock is configured correctly!")
        print("=" * 80)

        # Test invoking a model
        print("\n🧪 Testing model invocation...")
        try:
            runtime_client = boto3.client("bedrock-runtime", region_name="us-east-1")

            # Try Claude 3.5 Sonnet
            response = runtime_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-06-01",
                        "max_tokens": 100,
                        "messages": [
                            {"role": "user", "content": "Say 'Hello from Bedrock!'"}
                        ],
                    }
                ),
            )

            result = json.loads(response["body"].read())
            print("\n✅ Model Test Successful!")
            print(f"   Response: {result['content'][0]['text'][:50]}...")

        except Exception as e:
            print(f"\n⚠️ Model invocation failed: {e}")
            print("   This is normal if the model isn't enabled in your AWS account.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure AWS credentials are configured: aws configure")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
