from models_layer.training.train_price_model import train_price_model
from models_layer.training.train_affordability import compute_affordability_model
from models_layer.training.train_safety import compute_safety_model
from models_layer.training.train_livability import compute_livability_model

def main():
    print("Starting Model Training Pipeline...")
    train_price_model()
    compute_affordability_model()
    compute_safety_model()
    compute_livability_model()
    print("Pipeline Complete.")

if __name__ == "__main__":
    main()
