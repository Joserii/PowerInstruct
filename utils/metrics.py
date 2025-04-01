import time
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class MetricsCollector:
    start_time: float = field(default_factory=time.time)
    total_tokens: Dict[str, int] = field(default_factory=lambda: {"prompt": 0, "completion": 0})
    step_times: Dict[str, float] = field(default_factory=dict)
    iterations: List[Dict] = field(default_factory=list)
    final_accuracy: float = 0.0
    config: Dict = field(default_factory=dict)

    
    def start_step(self, step_name: str):
        """Start timing a step"""
        self.step_times[step_name] = time.time()
    
    def end_step(self, step_name: str):
        """End timing of a certain step"""
        if step_name in self.step_times:
            elapsed = time.time() - self.step_times[step_name]
            self.step_times[step_name] = elapsed
            return elapsed
        return 0
    
    def add_tokens(self, prompt_tokens: int, completion_tokens: int):
        """Add token count"""
        prompt_tokens = int(prompt_tokens) if prompt_tokens is not None else 0
        completion_tokens = int(completion_tokens) if completion_tokens is not None else 0
        self.total_tokens["prompt"] += prompt_tokens
        self.total_tokens["completion"] += completion_tokens

    def set_config(self, args):
        """Record experimental configuration parameters"""
        # Convert Namespace to dictionary
        if hasattr(args, '__dict__'):
            args_dict = vars(args)
        else:
            args_dict = args
            
        self.config = {
            "experiment_settings": {
                "model_codegen": args_dict.get("model_codegen", ""),
                "model_datagen": args_dict.get("model_datagen", ""),
                "max_iterations": args_dict.get("max_iterations", 0),
                "target_accuracy": args_dict.get("target_accuracy", 0.0),
                "batch_size": args_dict.get("batch_size", 0),
                "data_path": args_dict.get("total_data_dir", ""),
                "output_dir": args_dict.get("output_dir", ""),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
    
    def get_total_time(self):
        """Get the total running time"""
        return time.time() - self.start_time
    
    def get_metrics_report(self):
        """Generate a complete metrics report"""
        total_tokens = sum(self.total_tokens.values())
        report = {
            "experiment_config": self.config,
            "execution_metrics": {
                "total_time": f"{self.get_total_time():.2f}s",
                "step_times": {k: f"{v:.2f}s" for k, v in self.step_times.items()},
            },
            "token_metrics": {
                "total_tokens": self.total_tokens,
                "total_token_count": total_tokens,
            },
            "iteration_metrics": {
                "total_iterations": len(self.iterations),
                "iterations": self.iterations,
                "final_accuracy": f"{self.final_accuracy:.4f}",
            }
        }
        
        # Add iteration progress summary
        if self.iterations:
            report["iteration_metrics"].update({
                "initial_accuracy": f"{self.iterations[0]['accuracy']:.4f}",
                "best_accuracy": f"{max(iter['accuracy'] for iter in self.iterations):.4f}",
                "average_accuracy": f"{sum(iter['accuracy'] for iter in self.iterations)/len(self.iterations):.4f}",
                "accuracy_improvement": self._calculate_accuracy_improvement()
            })
        
        return report
    
    def add_iteration(self, iteration: int, accuracy: float, failed_cases: int):
        """Record information for each iteration"""
        self.iterations.append({
            "iteration": iteration,
            "accuracy": accuracy,
            "failed_cases": failed_cases,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def set_final_accuracy(self, accuracy: float):
        """Set the final accuracy"""
        self.final_accuracy = accuracy

    def _calculate_accuracy_improvement(self):
        """Calculation accuracy improved"""
        if not self.iterations:
            return "0.00%"
        initial = self.iterations[0]['accuracy']
        final = self.final_accuracy
        improvement = ((final - initial) / initial) * 100 if initial > 0 else 0
        return f"{improvement:+.2f}%"
    

