import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from catalogue.models import ProductModel, ProductVisualEmbedding
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API key found!")
    exit(1)

genai.configure(api_key=api_key)

# We will just generate an embedding based on the product description and attributes
# Since running Gemini Vision on 1000s of images would be slow, we use the rich text metadata 
# for the DB products, which is very similar to what Gemini Vision extracts!

def get_product_description(product):
    desc = f"Name: {product.name}. Category: {product.category.name if product.category else 'None'}."
    if product.description:
        desc += f" Description: {product.description}."
    tags = ", ".join([ta.tag.name for ta in product.tag_assignments.all()])
    if tags:
        desc += f" Tags: {tags}."
    return desc

products = ProductModel.objects.all()
print(f"Generating embeddings for {products.count()} products...")

for product in products:
    try:
        desc = get_product_description(product)
        embed_response = genai.embed_content(
            model="models/gemini-embedding-2",
            content=desc,
            task_type="retrieval_document",
        )
        embedding = embed_response['embedding']
        
        obj, created = ProductVisualEmbedding.objects.update_or_create(
            product=product,
            defaults={'embedding': embedding}
        )
        print(f"[{'Created' if created else 'Updated'}] Embedding for Product ID {product.id}")
    except Exception as e:
        print(f"Error on Product ID {product.id}: {e}")

print("Done!")
