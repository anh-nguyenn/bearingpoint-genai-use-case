import spacy
from faker import Faker
import re

# Download and load the SpaCy model
# spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Initialize Faker
fake = Faker()

# Dictionary to store original entities for unmasking
entity_dict = {}

def mask_pii(text):
    global entity_dict
    entity_dict = {}  # Reset the dictionary for each call
    doc = nlp(text)
    masked_text = text

    # Iterate over the entities detected by SpaCy
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            # Create a unique mask for each entity
            mask = f"***{ent.label_}_{len(entity_dict)}***"
            entity_dict[mask] = ent.text
            masked_text = masked_text.replace(ent.text, mask)
    
    # Mask 12-digit account numbers
    masked_text = re.sub(r'\b\d{12}\b', '****-****-****', masked_text)
    return masked_text

def unmask_pii(text_blocks):
    if isinstance(text_blocks, list):
        # Extract text from each TextContentBlock and join into a single string
        text = " ".join(block.text.value for block in text_blocks)
    else:
        text = text_blocks  # Assume text_blocks is already a string if not a list

    unmasked_text = text

    # Replace each mask with its original entity
    for mask, original in entity_dict.items():
        unmasked_text = unmasked_text.replace(mask, original)
    
    # Example unmasking for 12-digit account numbers (use secure method in production)
    unmasked_text = unmasked_text.replace('****-****-****', '1234-5678-9101')
    return unmasked_text



# Example usage
# example_text = "Jerry from Tesla has an account number 123456789012."
# masked_text = mask_pii(example_text)
# print("Masked:", masked_text)
# unmasked_text = unmask_pii(masked_text)
# print("Unmasked:", unmasked_text)
