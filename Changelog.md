## 0.0.36
+ Fixed crash when using `PIL.Image` values returned by edge predictors.
+ Updated to Function C 0.0.19.

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