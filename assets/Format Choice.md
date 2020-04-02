# Quick assessment of compression length

## Goal

- Short packed format
- Can be embedded in a text without tripping any editor

```txt
original (447 full utf-8 chars):
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

base64: (597 chars, 100.0%)
TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXBpc2ljaW5nIGVsaXQsIHNlZCBkbyBlaXVzbW9kCnRlbXBvciBpbmNpZGlkdW50IHV0IGxhYm9yZSBldCBkb2xvcmUgbWFnbmEgYWxpcXVhLiBVdCBlbmltIGFkIG1pbmltIHZlbmlhbSwKcXVpcyBub3N0cnVkIGV4ZXJjaXRhdGlvbiB1bGxhbWNvIGxhYm9yaXMgbmlzaSB1dCBhbGlxdWlwIGV4IGVhIGNvbW1vZG8KY29uc2VxdWF0LiBEdWlzIGF1dGUgaXJ1cmUgZG9sb3IgaW4gcmVwcmVoZW5kZXJpdCBpbiB2b2x1cHRhdGUgdmVsaXQgZXNzZQpjaWxsdW0gZG9sb3JlIGV1IGZ1Z2lhdCBudWxsYSBwYXJpYXR1ci4gRXhjZXB0ZXVyIHNpbnQgb2NjYWVjYXQgY3VwaWRhdGF0IG5vbgpwcm9pZGVudCwgc3VudCBpbiBjdWxwYSBxdWkgb2ZmaWNpYSBkZXNlcnVudCBtb2xsaXQgYW5pbSBpZCBlc3QgbGFib3J1bS4K

ascii85: (559 chars, 93.6%)
9Q+r_D'3P3F*2=BA8c:&EZfF;F<G"/ATTIG@rH7+ARfgnFEMUH@:X(kBlduuBl7Q+ASc(&/0K"FA0>E$+D#80F)>i+$?TirE,Tb>Bl7EpA8,RsDKI"DF<GC.@W-9u+D#X;A8c:&Eb-A1@:sId+CT)#EHP\B+B<M+ASu4!+CSe'D/!m%D'4"5DJ<Nr/.-B>BlbD7Df^#@F^uV+G\(o*Blmd*Bl@l3F_kl&D.@K,CggdkEbTS;DJ=0++E_cK@;KXtF_Pe;AU#>/@3B&uD/F3%D[KumDKBB/F^]AE+@L?dF!+n6FCcS/EclD6+CoD,DfQt7DBNt2E,oN'ASu$iEbTV<Bl5&:DesQ8FCB9&+Eh=4BlkJ/F)tn"@qfaqF_r73Des?4AKYQ,+D,b/Bjl*+DKTc3@3BMtEbSs(F`K)W7<i<RE-,Z6EZfF;DKI">@q/qY@psI%@s)a)A79RgF<GI>D@1?'DeW`nDKIEPF*2AB+DG^9@s)U,@3BQ4Bcq>+Anbah@3B)lF(KB7DKI"<Des6(F<G"0Bl+u,A0>H)F<GC.@W-:0D(Y

urlencode: (591 chars 99.0%)
Lorem%20ipsum%20dolor%20sit%20amet%2c%20consectetur%20adipisicing%20elit%2c%20sed%20do%20eiusmod%0atempor%20incididunt%20ut%20labore%20et%20dolore%20magna%20aliqua.%20Ut%20enim%20ad%20minim%20veniam%2c%0aquis%20nostrud%20exercitation%20ullamco%20laboris%20nisi%20ut%20aliquip%20ex%20ea%20commodo%0aconsequat.%20Duis%20aute%20irure%20dolor%20in%20reprehenderit%20in%20voluptate%20velit%20esse%0acillum%20dolore%20eu%20fugiat%20nulla%20pariatur.%20Excepteur%20sint%20occaecat%20cupidatat%20non%0aproident%2c%20sunt%20in%20culpa%20qui%20officia%20deserunt%20mollit%20anim%20id%20est%20laborum.

gzip|base64: (389 chars, 65.1%)
H4sICATbgF4AA3VuADWQwXFDMQhE76piC/D8KpJbrimASNhmRhKyBB6XH+Sf3ISAZfd96eQGGcsbiladWGKgxnZB1r44G5tPUJEhS7L0G7hKdBeX2ACLr6YlGbcR29KzFCneDW6o9BP6YDu1GY1unUBVHk4Hvg3cpYU4muzHM0pql/RwWei6bHoBv3hmMTLRDq+VWtZTeQ+FqX3pLSkjhsEUzlt40vROEKfswMeWJDeGTA8nZ1jpmDwm37kXnpE8Pp5afcQ5DjuRFLwWpyy1/iOKQI6r34QMfRvCoBmFzwOfr8zD2DfHYKA5E+eYyz6kkO0N7WlMlcJ9U9yk4mj2OggRAXq9BmZC4cVzd5vWbYM2IAkc64+rtyOlX8+tOYjAAQAA

./huffcode -i somefile | base64 -w0   (https://github.com/drichardson/huffman): (449 chars, 75.2%)
AAAAHQAAAcAKBh4gAwUsB24uBz5ECX4ARQl+AUwK/gFVCv4DYQQBYgcOYwULZAUHZQQPZgdOZwcoaAn+AGkDBGwEAG0FG24ECm8ECXAFGHEGCHIEAnMFF3QEA3UEBnYHaHgHLv6l/C7xtd2TkNLLaewfd1fq/TU/Jo1DzMtFRfWB4+7905N92t15vPmNU0pdPDymU5tCOFK+Pz0JKd8dKI0GELHw1f/pK3fjdFO5i35lbLeHGG8174idvutlcWKYWgOIvbIQjhTeKi9r0wAiRtx39aMr986T3kq9j1iMr36Mt2HzpZh8T0JKqZXH8v5ezwun1KITDE/MF/3A6d/73iKA7Z6ElO9bnYZiTNUAojiEMSa++nWtx/MmvdRprhW/YroM88TEVFM9LMnzOu5e0ym1ywBHEWPT6eRi9Px9MZ3uBOA0lLs8/TuFcKTY9nke

zip - somefile | base64 -w0: (599 chars, 100.0%)
UEsDBBQACAAIALSLfVAAAAAAAAAAAMABAAAGABwAYXBwL3VuVVQJAAME24BeLduAXnV4CwABBAAAAAAEAAAAADWQwXFDMQhE76piC/D8KpJbrimASNhmRhKyBB6XH+Sf3ISAZfd96eQGGcsbiladWGKgxnZB1r44G5tPUJEhS7L0G7hKdBeX2ACLr6YlGbcR29KzFCneDW6o9BP6YDu1GY1unUBVHk4Hvg3cpYU4muzHM0pql/RwWei6bHoBv3hmMTLRDq+VWtZTeQ+FqX3pLSkjhsEUzlt40vROEKfswMeWJDeGTA8nZ1jpmDwm37kXnpE8Pp5afcQ5DjuRFLwWpyy1/iOKQI6r34QMfRvCoBmFzwOfr8zD2DfHYKA5E+eYyz6kkO0N7WlMlcJ9U9yk4mj2OggRAXq9BmZC4cVzd5vWbYM2IAkc64+rtyOlX1BLBwjPrTmIDgEAAMABAABQSwECHgMUAAgACAC0i31Qz605iA4BAADAAQAABgAYAAAAAAABAAAApIEAAAAAYXBwL3VuVVQFAAME24BedXgLAAEEAAAAAAQAAAAAUEsFBgAAAAABAAEATAAAAF4BAAAAAA

require "zlib"; File.write('/tmp/def', Zlib::Deflate.deflate(data_to_compress)) | base64 -w0 (for python see https://stackoverflow.com/q/1089662/4007237): (370 chars, 62.0%)
eJw1kMFxQzEIRO+qYgvw/CqSW64pgEjYZkYSsgQelx/kn9yEgGX3fenkBhnLG4pWnVhioMZ2Qda+OBubT1CRIUuy9Bu4SnQXl9gAi6+mJRm3EdvSsxQp3g1uqPQT+mA7tRmNbp1AVR5OB74N3KWFOJrsxzNKapf0cFnoumx6Ab94ZjEy0Q6vlVrWU3kPhal96S0pI4bBFM5beNL0ThCn7MDHliQ3hkwPJ2dY6Zg8Jt+5F56RPD6eWn3EOQ47kRS8Fqcstf4jikCOq9+EDH0bwqAZhc8Dn6/Mw9g3x2CgORPnmMs+pJDtDe1pTJXCfVPcpOJo9joIEQF6vQZmQuHFc3eb1m2DNiAJHOuPq7cjpV8/yqUY 
```