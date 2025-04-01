#!/bin/bash
for model_codegen in "o1-preview-0912" "o1-mini-0912" "gpt-4o-0806" "qwen2.5-7b-instruct" "qwen2.5-coder-7b-instruct" "qwen2.5-coder-32b-instruct"
do
    python client/powerInstruct.py \
        --max_iterations 3 \
        --max_failures 2 \
        --min_accuacy 0.95 \
        --delta_accuracy 0.005 \
        --test_sample_ratio 0.3 \
        --model_codegen $model_codegen \
        --model_datagen "qwen2.5-7b-instruct" \
        --api_url "http://localhost:5000/analyze" \
        --clean_url "http://localhost:5000/clean" 
done