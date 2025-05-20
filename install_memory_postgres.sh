#!/bin/bash
echo "🔧 Setting up AI Test Runner memory components..."
pip install chromadb sentence-transformers psycopg2-binary openai python-dotenv

echo "✅ Dependencies installed."
echo "📁 Place the extracted files into your NS_AITester project structure:"
echo "  - oracle/use_cases.py"
echo "  - services/vector_store.py"
echo "  - services/test_case_storage.py"
