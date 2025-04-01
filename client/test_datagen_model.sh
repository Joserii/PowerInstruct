#!/bin/bash
for model_datagen in "o3-mini-2025-01-31"
do
    python client/powerInstruct.py \
        --max_iterations 3 \
        --max_failures 2 \
        --min_accuacy 0.95 \
        --delta_accuracy 0.005 \
        --test_sample_ratio 0.3 \
        --model_codegen "claude37_sonnet" \
        --model_datagen $model_datagen \
        --api_url "http://localhost:5000/analyze" \
        --clean_url "http://localhost:5000/clean" 
done