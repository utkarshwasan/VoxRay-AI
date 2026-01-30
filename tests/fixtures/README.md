# Test Fixtures

This directory contains sample files for backward compatibility testing.

## Required Fixtures

- `sample_xray.png` - Sample X-ray image for testing `/predict/image` endpoint
- `sample_audio.wav` - Sample audio file for testing `/transcribe/audio` endpoint

## How to Add Fixtures

### Sample X-ray

Copy any X-ray image from the test dataset:

```powershell
Copy-Item "consolidated_medical_data\test\06_PNEUMONIA\<any-image-file>" "tests\fixtures\sample_xray.png"
```

### Sample Audio

Record a short audio clip or use any `.wav` file:

```powershell
Copy-Item "<path-to-audio.wav>" "tests\fixtures\sample_audio.wav"
```

## Test Behavior

- **With fixtures:** Tests run fully and verify endpoint responses
- **Without fixtures:** Tests skip gracefully with clear messages

This is intentional - the tests are designed to work in CI/CD environments where PHI (Protected Health Information) cannot be stored.

## Note on PHI

**Do not commit actual patient data to this directory.** Use synthetic or anonymized test images only.
