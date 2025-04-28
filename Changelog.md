## 0.0.51
*INCOMPLETE*

## 0.0.50
+ Fixed import errors in `fxn.compile` module.

## 0.0.49
+ Fixed import errors in `fxn.beta` module.

## 0.0.48
+ Added `beta.LiteRTInferenceMetadata` class to lower PyTorch models for inference with LiteRT (fka TensorFlow Lite).
+ Refactored `beta.GGUFInferenceMetadata` class to `beta.LlamaCppInferenceMetadata`.
+ Upgraded to Function 0.0.35.

## 0.0.47
+ Fixed `Sandbox.upload_file` function failing to upload files when `from_path` is not an absolute path.
+ Fixed `Sandbox.upload_directory` function failing to upload files when `from_path` is not an absolute path.

## 0.0.46
+ Added `metadata` parameter in `@compile` decorator to provide metadata to the compiler.
+ Added `beta.CoreMLInferenceMetadata` class to lower PyTorch models for inference on iOS, macOS, and visionOS with CoreML.
+ Added `beta.ONNXInferenceMetadata` class to lower PyTorch models to ONNX for inference.
+ Added `beta.ONNXRuntimeInferenceSessionMetadata` class to lower ONNXRuntime inference sessions for inference.
+ Added `beta.GGUFInferenceMetadata` class to lower GGUF models for LLM inference.

## 0.0.45
+ Added `fxn source` CLI command to retrieve the native source code for a given prediction.
+ Added `--overwrite` flag in `fxn compile` CLI command to overwrite existing predictor before compiling.

## 0.0.44
+ Added `trace_modules` argument in `@compile` decorator to opt specific modules into tracing and compilation.
+ Added `targets` argument in `@compile` decorator for specifying targets to compile for.
+ Fixed prediction error when prediction output includes a `PIL.Image`.
+ Refactored `fxn.predictions.stream` method to return an `Iterator` instead of `AsyncIterator`.
+ Refactored `Acceleration` enumeration to string literal type.
+ Refactored `RemoteAcceleration` enumeration to string literal type.

## 0.0.43
+ Added `fxn compile` CLI command for access to the Function compiler proof of concept.
+ Added `fxn archive` CLI command for archiving predictors.
+ Added `fxn delete` CLI command for deleting predictors.
+ Refactored `PredictorStatus.Provisioning` enumeration member to `Compiling`.

## 0.0.42
+ Added `fxn.beta.predictions.remote.create` method for creating predictions on remote GPU servers.

## 0.0.41
+ Added support for streaming predictions.
+ Added `fxn.predictions.ready` to check whether a predictor has been preloaded.
+ Added `verbose` parameter in `fxn.predictions.create` method to print prediction progress.
+ Added `--quiet` option in `fxn predict` CLI action to suppress verbose logging.
+ Fixed prediction errors when making passing in `str`, `list`, or `dict` arguments.
+ Fixed invalid data type error when prediction returns a greyscale image.
+ Fixed prediction error in CLI when passing file path as prediction input value.
+ Refactored `Acceleration.Default` enumeration member to `Acceleration.Auto`.
+ Removed `Profile` type. Use `User` type instead.
+ Updated to Function C 0.0.31.

## 0.0.40
+ Fixed errors when `Function` client is created for the first time on a new device.
+ Updated to Function C 0.0.29.

## 0.0.39
+ Fixed errors when `Function` client is created on Windows.

## 0.0.38
+ Function now supports Linux, across `x86_64` and `arm64` architectures.

## 0.0.37
+ Added `fxn --explore` CLI action to explore predictions on [fxn.ai](https://fxn.ai/explore).

## 0.0.36
+ Added `Acceleration.Default` enumeration constant.
+ Added `Acceleration.GPU` enumeration constant for running predictions on the GPU.
+ Added `Acceleration.NPU` enumeration constant forn running predictions on the neural processor.
+ Fixed crash when using `PIL.Image` values returned by edge predictors.
+ Updated to Function C 0.0.26.
+ Removed `Value` type.
+ Removed `PredictorType` enumeration.
+ Removed `fxn.predictors.create` method for creating predictors. [Apply](https://fxn.ai/waitlist) for early access to the new experience.
+ Removed `fxn.predictions.to_object` method.
+ Removed `fxn.predictions.to_value` method.
+ Removed `Predictor.type` field.
+ Removed `Predictor.acceleration` field.
+ Removed `Prediction.type` field.
+ Removed `Acceleration.A40` enumeration constant.
+ Removed `Acceleration.A100` enumeration constant.
+ Removed `fxn create` CLI function.
+ Removed `fxn delete` CLI function.
+ Removed `fxn list` CLI function.
+ Removed `fxn search` CLI function.
+ Removed `fxn retrieve` CLI function.
+ Removed `fxn archive` CLI function.
+ Removed `fxn env` CLI function group.
+ Removed `--raw-outputs` option from `fxn predict` CLI function.
+ Function now requires Python 3.10+.

## 0.0.35
+ Updated to Function C 0.0.18.

## 0.0.34
+ Fixed `fxn` import error caused by `fxn.predictions.stream` function.

## 0.0.33
+ Fixed error in `fxn.predictors.retrieve` function.

## 0.0.32
+ Added missing native libraries.

## 0.0.31
+ Added experimental support for making on-device predictions.
+ Added `PredictionResource.name` field for handling prediction resources with required file names.

## 0.0.30
+ Fixed data type inference when making predictions.

## 0.0.29
+ Minor fixes and improvements.

## 0.0.28
+ Added `fxn create --cloud` CLI shorthand flag for setting the predictor type to `PredictorType.Cloud`.
+ Added `fxn create --edge` CLI shorthand flag for setting the predictor type to `PredictorType.Edge`.
+ Removed `AccessMode.Protected` access mode. Use `AccessMode.Public` or `AccessMode.Private` instead.
+ Removed `fxn.types.tag.parse_tag` function. Use `Tag.from_str` class method instead.
+ Removed `fxn.types.tag.serialize_tag` function. Use `str(Tag)` instead.

## 0.0.27
+ Added support for streaming when making predictions with Function CLI.
+ Added `PredictionResource.type` field for inspecting the type of a prediction resource.
+ Fixed pydantic forward reference errors when constructing `Signature` and `Predictor` instances.
+ Fixed `model_dump` error when making predictions in Google Colab due to outdated `pydantic` dependency.
+ Refactored `fxn.predictions.create` method to accept an `inputs` dictionary instead of relying on keyword arguments.

## 0.0.26
+ Added support for serializing `BytesIO` instances in `fxn.predictions.to_value` method.
+ Refactored `fxn.predictions.to_value` method to `to_object` for clarity.
+ Refactored `fxn.predictions.from_value` method to `to_value` for clarity.
+ Updated `fxn.predictions.to_object` method to always use aliased field names when serializing Pydantic types.

## 0.0.25
+ Fixed JSON serialization errors when using the CLI to perform some operations.

## 0.0.24
+ Added `Function` client class to replace functions on individual API types.
+ Refactored `Value.from_value` method to `fxn.predictions.from_value`.
+ Refactored `Value.to_value` method to `fxn.predictions.to_value`.
+ Changed `Parameter.default_value` field type to `Value`.
+ Removed `CloudPrediction` class. Use `Prediction` class instead.
+ Removed `EdgePrediction` class. Use `Prediction` class instead.

## 0.0.23
+ Added `AccessMode.Protected` enumeration member for working with protected predictors.
+ Added `pydantic` as an explicit dependency.

## 0.0.22
+ Added `Prediction.stream` method for creating streaming predictions.

## 0.0.21
+ Fixed `Value.from_value` method raising exception when serializing a list of Pydantic models.

## 0.0.20
+ Added support for serializing Pydantic models in `Value.from_value` method.

## 0.0.19
+ Added `Parameter.schema` field for inspecting the JSON schema for `dict` and `list` parameters.
+ Fixed `UnboundLocalError` when calling `Value.from_value` method with unsupported value type.

## 0.0.18
+ Switched to more ergonomic loading indicator in CLI.

## 0.0.17
+ Refactored `Predictor.readme` field to `card`.

## 0.0.16
+ Add loading indicator when making predictions in CLI.

## 0.0.15
+ Fixed `Predictor.search` method raising error.

## 0.0.14
+ Added `Dtype.null` constant for working with `None` prediction values.

## 0.0.13
+ Refactored `Feature` class to `Value` for improved clarity.
+ Refactored `UploadType.Feature` enumeration member to `UploadType.Value`.

## 0.0.12
+ Added `Predictor.readme` field for inspecting the readme of a predictor notebook.

## 0.0.11
+ Added `EnumerationMember` class for working with parameters that are enumeration values.
+ Added `Parameter.enumeration` field for inspecting parameters which hold enumeration values.
+ Added `Parameter.default_value` field for inspecting the default value of a predictor parameter.
+ Renamed `Dtype._3d` data type to `model`.
+ Removed `Parameter.string_default` field. Use `Parameter.default_value` field instead.
+ Removed `Parameter.int_default` field. Use `Parameter.default_value` field instead.
+ Removed `Parameter.float_default` field. Use `Parameter.default_value` field instead.
+ Removed `Parameter.bool_default` field. Use `Parameter.default_value` field instead.

## 0.0.10
+ Added `Feature.from_value` class method for creating `Feature` instances from plain Python values.
+ Added `Feature.to_value` method for converting a `Feature` instance to a plain Python value.
+ Added `Predictor.list` class method for listing a user's predictors.
+ Added `fxn list` CLI command for listing a user's predictors.
+ Removed `features` argument in `Prediction.create` method. Use `inputs` kwargs instead.
+ Removed `FeatureInput` class.

## 0.0.9
+ Added `EnvironmentVariable` class for managing predictor environment variables.
+ Added `fxn env` CLI command for managing predictor environment variables.
+ Added Function magics to customize how predictors are provisioned. Use `%load_ext fxn.magic` in your predictor notebook.
+ Fixed `Prediction.create` raising exception when the prediction resulted in an error.
+ Moved `fxn predictors` CLI commands to top-level. You can now use commands like `fxn create` directly.

## 0.0.8
+ Fixed `fxn predictors create` CLI command raising authentication error.

## 0.0.7
+ Fixed `fxn predictors create` CLI command raising error.

## 0.0.6
+ Fixed `fxn predictors create` CLI command raising error.

## 0.0.5
+ Added `Prediction` class for making predictions.
+ Added `fxn predict` CLI command for makong predictions.
+ Updated `Predictor.create` method `type` argument to be optional. Cloud predictors are now the default.

## 0.0.4
+ Added `Predictor.create` class method for creating predictors.
+ Added `fxn predictors create` CLI command for creating predictors.
+ Fixed `User.retrieve` method raising exception when retrieving current user.
+ Fixed `fxn auth logout` CLI command erroring when user was already logged out.

## 0.0.3
+ Added `Signature` type for inspecting predictor signatures.
+ Added `Parameter` type for inspecting predictor signature parameters.
+ Added `Acceleration` enumeration for specifying predictor acceleration.
+ Added `PredictorType` enumeration for specifying predictor type.

## 0.0.2
+ Added Function API types and services.
+ Added command line interface. Run `fxn` in your terminal.

## 0.0.1
+ First pre-release.