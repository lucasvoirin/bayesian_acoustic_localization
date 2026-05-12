import subprocess

scripts = [
    "./src/arrayReconstruction_1_simulations.py",
    "./src/arrayReconstruction_2_resultsAnalysis.py",
    "./src/fieldTest_1_formatMetadata.py",
    "./src/fieldTest_2_arrayReconstruction.py",
    "./src/fieldTest_3_localization.py",
    "./src/fieldTest_4_resultsAnalysis.py",
    "./figures/arrayReconstruction_arrayMetrics.py",
    "./figures/arrayReconstruction_localizationMetrics.py",
    "./figures/arrayReconstruction_arrayExample.py",
    "./figures/fieldTest_histErrorFm.py",
    "./figures/fieldTest_array.py",
]

for script in scripts:
    
    result = subprocess.run(
        ["python3", script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"{script}: OK")
    else:
        print(f"{script}: ERROR")
        print(result.stderr)
        break
