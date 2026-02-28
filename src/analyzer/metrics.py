import pandas as pd

def parse_simulation_metrics(metrics: dict, algo_name: str) -> pd.DataFrame:
    """
    Parses simulation metrics into a unified Pandas DataFrame for visualization.
    """
    row = {
        'Algorithm': algo_name,
        'Qubits Required': metrics.get('qubits_required', 0),
        'Circuit Depth': metrics.get('depth', 0),
        'Total Gates': metrics.get('total_gates', 0),
        'Execution Time (s)': round(metrics.get('execution_time_seconds', 0), 4)
    }
    
    df = pd.DataFrame([row])
    return df

def generate_noise_comparison(success_probs: list, noise_levels: list) -> pd.DataFrame:
    """
    Maps success probabilities against varying noise levels.
    """
    return pd.DataFrame({
        'Noise Probability': noise_levels,
        'Success Probability': success_probs
    })
