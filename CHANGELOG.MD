# Changelog

## v1.5.1 (2024/09/17)
### 🐛 Fixes
- [Fix issue with environment sensor with multiple properties](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6719ceec7de5bf6bab4152d8ff2e8eb0e22ae483) - @RogerSelwyn

### 🔖 Release
- [Release v1.5.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/8de5a66484112a7a3f6347be69766255a06d6cdd) - @RogerSelwyn

## v1.5.0 (2024/09/17)
### 🐛 Fixes
- [Handle re-auth correctly](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a75913020d4e83d46d653b6d99107413557f60b3) - @RogerSelwyn
- [Fix lack of support of webhook property alert](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4bdf83246bdbc95bb70ce717d0d8074b16f67772) - @RogerSelwyn
- [Fix incorrect throttling](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/29504ba0cc36897c66ed410db7a19edcf6265c47) - @RogerSelwyn
- [Fix corrected calculatedat from pyhomelink](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ccc1a15c170f4b8b54def693e84cf10784541751) - @RogerSelwyn

### 🧰 Maintenance
- [Minor formatting](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/16ac28c27acce3140e7ff4770e4a1d29113327e8) - @RogerSelwyn
- [Minor re-structure to remove unneeded exception protection](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3781e63e33bfc8fcf1a6b49ff4b4813dc45967d5) - @RogerSelwyn
- [Remove redundant code](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ad407ee7edcd1f6f4f24b708a120b4e5c003e9e1) - @RogerSelwyn
- [Tweak throttling to give control](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/8e3fc021ae66d7d5827c2271eb074d01faca8e4d) - @RogerSelwyn

### ⬆️ Dependencies
- [Bump pyhomelink to 0.2.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c5eac3fecf460ebbc7664896e6514f48652114ae) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/b567c506d2a0d882a5a47a6d3c3cf58a0e447127) - @actions-user
- [build(deps): bump ruff from 0.5.5 to 0.6.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/260af61c605d790c64c39e2763d999c1eee2786d) - @dependabot[bot]
- [build(deps): bump ruff from 0.6.3 to 0.6.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fcc8201eb9b77e09ec81fcf28605fb7bfa6091ba) - @dependabot[bot]

### 📚 Documentation
- [Update README.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/323da02c06829920d2d5f745ac9bd9e4517ac49a) - @RogerSelwyn

### ✅ Test
- [Add initial config_flow testing](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/bd20862cacc799770fba9bff1c44c475fd9350ab) - @RogerSelwyn
- [Sort out linting issues](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4f953d959a59510bb87e96d1f2d1b9f359ab769d) - @RogerSelwyn
- [Add pyproject.toml matching HA for linting/formatting](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/99ae15ae8bf4b3d794710b5ffc1873c7911f753e) - @RogerSelwyn
- [Format testing code with Ruff](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/226d59ec6f43130ad924fd4bf180623f4b8e0aaf) - @RogerSelwyn
- [Correct pyproject.toml for Ruff](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0f689c702408f2a3bf78a0ffbc1253817abecb3b) - @RogerSelwyn
- [Ruff deal with Ruff errors :-(](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ceb30bbe34e834696ab125d7441fb2e65f32cde2) - @RogerSelwyn
- [Add some base setup testing](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2e703e679b82dd7ac05557d7289aa636c59d0057) - @RogerSelwyn
- [Add more testing for alerts via api](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/5bfe06f3036ea13e826d0593f7e6d720946b9ca7) - @RogerSelwyn
- [Add more testing around errors, webhooks and insights](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/baaa6db8d506018837ff69c80e71c87542f81fb2) - @RogerSelwyn
- [Add tests for Webhooks](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/93c92bcbf7c1129d95996c7df72f69df4d23aaa2) - @RogerSelwyn
- [Added final webhook tests](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a3c7d32847f406ceb594d8957eafd59249ba4b13) - @RogerSelwyn
- [Added MQTT testing - 95% commented out due to Mock issues](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/aeaff5aa40a22c9b0c275756b4b90a2347b64235) - @RogerSelwyn
- [Remove MQTT testing since it is deprecated in HomeLINK](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ca91cb5a1060a0994fe6f45a0101915b86c888bf) - @RogerSelwyn
- [Add testing action](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/9ad72fc4ce96855e62619b89cdf0329014cc96be) - @RogerSelwyn
- [Update test.yaml](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/9f392e4ed4ab1b289e190f17356c616c2c314da5) - @RogerSelwyn
- [Add more testing to fill gaps](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2622a2b87a99e1984d59a42a409aa6d552cd1bed) - @RogerSelwyn
- [Add readings tests (and restructure tests)](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/dfc157e62ba2098046004ce5077614425d540144) - @RogerSelwyn
- [Remove print statements](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/15cf384a03865925f5ac46d53ac5a403f3996323) - @RogerSelwyn

### 🔖 Release
- [Release v1.5.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c285fe57f5d0234c89903d67ddb538a589712a5d) - @RogerSelwyn

## v1.4.6 (2024/08/08)
### 🧰 Maintenance
- [Move coordinator setup code to new _async_setup method](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/d63c2db854b23678c8958531e41f92e9db08b99d) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.6](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/639ab982d9acebbbfb2c9c78bdcec8657dfa170c) - @RogerSelwyn

## v1.4.5 (2024/08/02)
### 🐛 Fixes
- [Handle situation where no existing readingdate](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/964418363aa797d93266cfa12b122de24b6fd7e8) - @RogerSelwyn

### 🧰 Maintenance
- [Add model_id to DeviceInfo](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/32b1f62c6cda1863956150d6af02bcc346f74e3a) - @RogerSelwyn
- [Bump minimum HA to 2024.8.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a49b1905896dd3c2f03ed70d2a80a91896d52242) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/24bc00a32d49fd192f2aba95badd6972b89100a9) - @RogerSelwyn


## v1.4.4 (2024/06/06)
### 🐛 Fixes
- [Gracefully handle situation where external url not set on HA for webhooks](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/966b4a17d89dc84759f8a256cc7b7283dcfa5a7f) - @RogerSelwyn

### 🧰 Maintenance
- [Migrate to new reauth method](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7e67faecae9f624dda8cd95dd01249680ffe822c) - @RogerSelwyn
- [Change to store runtime data in the config entry](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c1d27c90610257e5b62eea96334c672b91ca98ad) - @RogerSelwyn
- [Re-organise config data](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2726c4992fca3f74754f7490dfb839d1c0bed0e7) - @RogerSelwyn
- [Move calls to async_remove outside the thread](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f9d605c34facc530515c90e83b151a5bb158fa7d) - @RogerSelwyn
- [Import HA.util.dt as dt_util](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e1371139ec43fd9cdd811031a3d70a6121109cb2) - @RogerSelwyn

### 📚 Documentation
- [Update CHANGELOG.MD](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/831094222189f44f39818466d04336278485438a) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.4](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2458e5fa6115b8efb0ec5c0c44d448713b8a8464) - @RogerSelwyn

## v1.4.3 (2024/04/17)
### 🐛 Fixes
- [Fix issue with change in rest api serial number for Reading](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/765500cdd40caa4cd83b140819db225549b25c4b) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/23f4b9b75ad55dd6437563d1b1ccb93bb40024bd) - @RogerSelwyn

## v1.4.2 (2024/04/17)
### ⬆️ Dependencies
- [Bump pyhomelink to 0.1.11](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/bf3a56c91e960bc654c0e6f0b9d7cc7fa41aae51) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fa9c97c577f8c34ceff59b130e8fa0fc1779f61a) - @actions-user

### 🔖 Release
- [Release v1.4.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/51f26fb45caf50010d2577e408c0d6ea64e9a673) - @RogerSelwyn

## v1.4.1 (2024/03/06)
### 🧰 Maintenance
- [Add 'single_config_entry' to manifest](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e622d22a90c77a248c3cdd2157a8072723a83b89) - @RogerSelwyn

### 📚 Documentation
- [Update index](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/237ee11078b5f78a92330df9cb44ccb28cd6ab9b) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/bfbf9b0763d759fa0f7d3ad0735c57cb2d863e6f) - @RogerSelwyn

## v1.4.0 (2024/02/29)
### ✨ Enhancements
- [Add Webhook support](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e0a116a4a04c5fb09d2ddba85287b8fc07b43383) - @RogerSelwyn

### 📚 Documentation
- [Update MQTT docs to remove non-working example](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0c5bbd1e69a1ef765afa58c1d6af0f2e8bd8ca3c) - @RogerSelwyn
- [Correct MQTT docs](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2240114793477679a7773f973d6b07c89eee3fae) - @RogerSelwyn

### 🔖 Release
- [Release v1.4.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/9b8cc088f26f25756c1aaa62ae6aaca91b3018dd) - @RogerSelwyn

## v1.3.8 (2024/02/21)
### 🐛 Fixes
- [Fix issue where reading sensors would become unavailable](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/435b31c6437c008ef5af0baed0fbc0bee25508cd) - @RogerSelwyn

### 🔨 Maintenance
- [Update bug_report.yml](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f1f869b5a019f4f33f2338a73b3a08efefd7f2ea) - @RogerSelwyn

### 🔖 Release
- [Release v1.3.8](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f349b180168b5b215b43038e5d6d2eb5e5b20a66) - @RogerSelwyn

## v1.3.7 (2024/01/26)
### 🐛 Fixes
- [Fix insights not updating after initial load](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f1681816b3ab5c1e095876f0cd70d3503c9b28c8) - @RogerSelwyn

### 🔨 Maintenance
- [Correct 'type' of room insight](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/d14d5e475187cdc4c02f6c41b6b7ee73a8823e72) - @RogerSelwyn

### 🔖 Release
- [Release v1.3.7](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/583cc2c2c740facf8174303e88bfb113522cb2ae) - @RogerSelwyn

## v1.3.6 (2024/01/24)
### 🔨 Maintenance
- [Identify property/device insights from each other](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/21885844ee62c5a0edec8720ddfe44ffb61c8522) - @RogerSelwyn

### 🔖 Release
- [v1.3.6](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fa2cf22f88045ce806b31fe8b6f955ced2ae9045) - @RogerSelwyn

## v1.3.5 (2024/01/24)
### ✨ Enhancements
- [Add optional Insight sensors for environment devices](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2d5cb7e2d8891fc7b43bb354c2d763525dd2275c) - @RogerSelwyn

### ⬆️ Dependencies
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2b7ae9d4477654a270deb4443039bda08c9c2327) - @actions-user

### 🔖 Release
- [Auto update manifest.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3a8837781f4435eae00f79d1ccfc86b6533ef197) - @actions-user
- [Release v1.3.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4826eb5e1f940a1b1c59462e49842b3508293291) - @RogerSelwyn

## v1.3.4 (2023/12/25)
### 🔨 Maintenance
- [Config flow tweaks](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e5365d5e68d40ba1673cfe1303b800c4f393f1af) - @RogerSelwyn
- [Remove deprecated constant](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/96474cb25d8a4de183d3cbfa14ada6efbd8814d2) - @RogerSelwyn
- [Disable warning](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a63b1bb672e88675def23038f82944f560c7eae9) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.3.4](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3a8837781f4435eae00f79d1ccfc86b6533ef197) - @actions-user

## v1.3.3 (2023/12/12)
### 🐛 Fixes
- [Environment property element being deleted and recreated on every restart](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2f6ac18083f25bfd94fbf2cb5e0896d1e85c1f6d) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.3.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1a251bb3a81f586936b02571d31bbe142d80fccd) - @RogerSelwyn

## v1.3.2 (2023/12/11)
### 🐛 Fixes
- [Stop reporting old events](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/889d515046c0520fd431a9ecef31a70e8307c447) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.3.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/9a6fbcaaf320ebf7ec815b00d43565bb44c9fe69) - @RogerSelwyn

## v1.3.1 (2023/12/11)
### 🔨 Maintenance
- [Improve alarmed_devices/rooms attributes](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/acd048d7a1ae03674482eee40895640e16933e2a) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.3.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1bcf2fbc7ecd30b3d17a4e80e2870e8078503ed2) - @RogerSelwyn

## v1.3.0 (2023/12/11)
### ✨ Enhancements
- [Separate upward reporting of fire/co alarm from environment.](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f5347a241104381ba620d26c9f83d867931145b4) - @RogerSelwyn
- [Split out alarm and environment top level reporting](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6904fad718f702716bf9432cf9ffb4cc9843cdc0) - @RogerSelwyn

### 🐛 Fixes
- [Correct error in previous change](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1b8d51379c261c064ad70af71c8971feb3cd94ef) - @RogerSelwyn

### 🔨 Maintenance
- [Improve mqtt reading handling](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1c3c6d20b9038c32bcbc62259a53c132474de337) - @RogerSelwyn
- [Sourcery recommended improvements](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f63b593daf74f504cad7c6465aa4691480a5de9d) - @RogerSelwyn

### ⬆️ Dependencies
- [Bump pyhomelink to 0.1.8](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/d305df5de3a3715369d58d070d2895030658dd83) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/24c47a97ec46e07611700cb557a1c0833b5ee691) - @actions-user

### 🔖 Release
- [Bump to v1.3.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a6fa4ada65294bb9031578ffd7cba8e2d23790ad) - @RogerSelwyn

## v1.2.1 (2023/11/21)
### ✨ Enhancements
- [Use mqtt for maintaining reading sensors](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1edf4c712401f3a708421c0a8cdd851e36a71224) - @RogerSelwyn

### 📚 Documentation
- [Update docs with env sensor type](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0bfccbd1b8a0b9824d11692919fcf2d2dbe3f03b) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.2.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/8319c8f10bc59b3845e3ea922fff808037879e70) - @RogerSelwyn

## v1.2.0 (2023/11/19)
### ✨ Enhancements
- [Add support for readings](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/54772df9aa3996263d13d6a37c16757be0624fbd) - @RogerSelwyn

### 🐛 Fixes
- [Fix error when new device added dynamically](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/35e3b5fb3e2be00af7f647cdb9ea7ba6658b7c61) - @RogerSelwyn
- [Correct invalid release version](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/59bc96521281c0d7949da7369f028f2f7591f97f) - @RogerSelwyn

### 🔨 Maintenance
- [Delete .github/stale.yml](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0409d6e72451d62173c64ef1244590738978b3e0) - @RogerSelwyn
- [Create stale.yaml](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/85f986e84c4918a01ee79c7edbd73cb072630b30) - @RogerSelwyn

### ⬆️ Dependencies
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e6ede62c81f471c8312e630a3ada4f0dbd7bf700) - @actions-user

### 🔖 Release
- [Auto update manifest.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/74ee7d1bfb666618e149a2e63d427f860d9bbabb) - @actions-user
- [Bump to v1.2.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ca7a98cd4714c7267ee1db4636595f3a698f7ec8) - @RogerSelwyn

## v1.1.3 (2023/11/07)
### 🐛 Fixes
- [Fix display of api error](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/bb9d601417d63c3036e2d7fbc1cbabf56e48ddb7) - @RogerSelwyn

### ⬆️ Dependencies
- [Bump pyhomelink to 0.1.6](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6e76a6a8119f6212570291fb40485ed3eda4d846) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fed120a838b76c988cef99ed4ee407a145ac3c13) - @actions-user

### 🔖 Release
- [Bump to v1.1.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c965bd46e155c87f633bfd1c931704b946403d00) - @RogerSelwyn

## v1.1.2 (2023/11/07)
### ✨ Enhancements
- [Add operational status and restructure attributes for device binary sensors](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0f866dfd0f61bc05b35b55d1c41e4d6179ce2601) - @RogerSelwyn

### 🐛 Fixes
- [Fix warning not being logged on api failure](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/887b3c3d8338f3ee61da004e5cbdd60bf28569cd) - @RogerSelwyn

### 🔨 Maintenance
- [Minor code improvement](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ced3e74077fe7e6cf601a47d4dc2e29f3c699422) - @RogerSelwyn
- [Add loggers to manifest.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1e3fb9f560207c3f0e38c16474a8c7229955bcc4) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.1.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/151fec44ca6c4403379209b286eee438fbfe4ae2) - @RogerSelwyn

## v1.1.1 (2023/10/24)
### 🔨 Maintenance
- [Reduce number of calls to HomeLINK API](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3625b4a1e670f9018bed30442361b11c12832d3a) - @RogerSelwyn
- [Reduce the number of valid eventtypes listed](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/cd84dd75b844353d7a8bf0ade1f20dada117676f) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/05cf76376c6f25dbd84ea0b323f2fd248f3e211f) - @actions-user

### 📚 Documentation
- [Update index.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/bd1f1242bc39f50af170d9dfb4255e857a5d594e) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.1.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1c98ce4860d4a7936b6e612489fbd43bbfa50eac) - @RogerSelwyn

## v1.1.0 (2023/10/23)
### ✨ Enhancements
- [Add experimental support for Environment Sensor and Insights](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/98fc5041c195b07c1856173c19e0e3b1bada6877) - @RogerSelwyn

### 🔨 Maintenance
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/49117e22be789015634133aa7eff4ba169792f16) - @actions-user

### 🔖 Release
- [Bump to v1.1.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fa08822a76f325e635fbc3ce9ec1e92fb29a884d) - @RogerSelwyn

## v1.0.6 (2023/10/22)
### ✨ Enhancements
- [Add more information to event entity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/385ebb5ae5a0df3a9e216840028a08b5b4f9840f) - @RogerSelwyn
- [Add further detail to event entity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/848a35269bc9e17f31c7bfa349f2f8adf8f29bdf) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.6](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/eab027d55956f3feb7b41d27648b668fdff3b54c) - @RogerSelwyn

## v1.0.5 (2023/10/22)
### 🐛 Fixes
- [Correctly build device info for event entities](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/73c2a3e394879643ff191ff5073ba3e7bcb6c259) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c1b4ebc791f187f55b8c6ed6252ed1379f5670bf) - @RogerSelwyn

## v1.0.4 (2023/10/21)
### ✨ Enhancements
- [Add action timestamp to event entities](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/943591c4a4e3fc5415b4a25556acf3a0b83b8bf2) - @RogerSelwyn

### 🔨 Maintenance
- [Remove unrequired imports](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1c8422075a9818f35a3624f4f15bf17c71bc4787) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.4](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e327ec189bc4194e0ef541774c17447e62bab21e) - @RogerSelwyn

## v1.0.3 (2023/10/21)
### 🐛 Fixes
- [Fix how alerts are handled, device operationstatus does not update](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/69a1fae8c08f07acc90799980ac2eec5375ca7f0) - @RogerSelwyn

### 🔨 Maintenance
- [Tidy up code](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/19b5afd8afb7385fd5351d28e355f9403c786db2) - @RogerSelwyn
- [Move ancilliary classes to helpers folder](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/dc031cd7781f438947f20414761b4dbf81a272cb) - @RogerSelwyn
- [More code tidy up](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7d1e703856a414b21c697e9f5d3572fe62991a6e) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c67cb2102b294c52336529e1f8a57b83d2d065dc) - @RogerSelwyn

## v1.0.2 (2023/10/10)
### 🐛 Fixes
- [Ensure latest event used](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/752ace8fd608d0ac24549947fdcb0de5216a25a0) - @RogerSelwyn
- [Fix issue where binary sensors not updating](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2564e42f53ffd5bea6a98df71117c047d308dc22) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/90738966cccc3fe7352b2146d87d7f996c67ed9c) - @RogerSelwyn

## v1.0.1 (2023/10/09)
### 🐛 Fixes
- [Fix registration for mqtt events by event entity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/81f8d73de7d97511dbe30deb2449a8b94247e868) - @RogerSelwyn

### 📚 Documentation
- [Update docs with event entity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/dbed32efa0cbb82d83c1200907dc878dc58e6619) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/26142f8e5e147d4df2cecf110a5e066147f08939) - @RogerSelwyn

## v1.0.0 (2023/10/09)
### ✨ Enhancements
- [Add event entities for MQTT events](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/dddc2dfc00b32c26ba65e1eaef3fef1c3a18a465) - @RogerSelwyn
- [Add config control for creating event entities](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c591730760d4dd60b547ed64f2e3fb25019709b6) - @RogerSelwyn

### 🔨 Maintenance
- [Handle (de)registration of mqtt handlers in a more HA manner](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c21b5653121b270412c4457fe547e28384c11845) - @RogerSelwyn
- [Remove redundant attribute](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6d483cd583c207360f4146744590394013a6a0ab) - @RogerSelwyn

### 📚 Documentation
- [Correct event example](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a2896d5bfd12daae386597a08d768a0e5b7c1411) - @RogerSelwyn

### 🔖 Release
- [Bump to v1.0.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/d5fa99d318a4b4f623136fee50ffa10a4a22eef7) - @RogerSelwyn

## v0.2.2 (2023/10/08)
### ✨ Enhancements
- [Add unsubscribe from MQTT on unload](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/953dfaad3fac3c0448fbabbf222bbbea6914b609) - @RogerSelwyn

### 🐛 Fixes
- [Fix invalid default topic entry](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6bf073e854e04525b72f5761d1a7bea184353f17) - @RogerSelwyn

### 🔨 Maintenance
- [Tidy up code around root_topic](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3f97bf6811b9cd756f4599bd5d83706d3209a10c) - @RogerSelwyn
- [Remove unrequired attribute](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4d06f5e60fc3d1c9c1668d44f596308a602b58d8) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e5f9f0b699973c460eb5697b84c2472116af0a8b) - @actions-user

### ⬆️ Depenencies
- [Bump pyhomelink to 0.1.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/9bfa4f03e264270d69d18a2ff4d4e491c002f924) - @RogerSelwyn

### 📚 Documentation
- [Update README.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/949c4bf3b543fe6e6260f2b3a0b708b7a358527d) - @RogerSelwyn
- [Update README.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f3443b42fdf2a6520cbe38a881bcb0b187006c96) - @RogerSelwyn
- [Update index.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1675ead664fdd1e320b4488a06e9295d0cd6ae1d) - @RogerSelwyn
- [Update README.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6c56c39ae78605e9cf7d0b8a78944c557186a5e9) - @RogerSelwyn
- [Update index.md](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/460de3d5d2ef716a117f46d0aa3b70406fd1b827) - @RogerSelwyn

### 🔖 Release
- [Bump to v0.2.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/5d96479da5a8c651ca875e341746fc4fe1392436) - @RogerSelwyn

## v0.2.1 (2023/10/01)
### 🐛 Fixes
- [Fix events not being raised as correct type](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/83ae10e95c5d1231a804e524796ebb4144a10ec0) - @RogerSelwyn

### 🔨 Maintenance
- [Minor code changes](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/80078e19e8555d2e5c80c224184f2a90a481425a) - @RogerSelwyn
- [Bump to v0.2.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/6e64701bd4923f39038747672059b3a5c3d7728e) - @RogerSelwyn

### 📚 Documentation
- [Add supported AICO devices types](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/cc5a070604a9fab1ec50f2f1743c88c637ae9204) - @RogerSelwyn
- [Docs correction](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/844c4433cd338749e840b69e879a0afbd78fa23c) - @RogerSelwyn

## v0.2.0 (2023/10/01)
### ✨ Enhancements
- [Added support for using HomeLINK MQTT](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/b899a969221313a1463fcd2b7cac7d9b86f47511) - @RogerSelwyn

### 🔨 Maintenance
- [Minor code tweaks](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/44aa3dda79a462b4c5cbce47f37add881881fd76) - @RogerSelwyn
- [Use provided root topic in configuration settings](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/749e9a9a69656f5a0b4ef1a216f950eaf6b3686f) - @RogerSelwyn
- [Bump to v0.2.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1caae03f6a4fb7bb803c0f54cafd8471dc0ba024) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ac65dac630bbcf5f3c58c194b4a45d018d1dc9ad) - @actions-user

### 📚 Documentation
- [Update Read Me](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1749b7bd5e6e75086e842e01cd01e32998621e85) - @RogerSelwyn
- [Update docs for new HomeLINK MQTT capability](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/54fce760dc762ba3f3f51868ec1c5315b34e8f2b) - @RogerSelwyn

## v0.1.6 (2023/09/28)
### ✨ Enhancements
- [Substantially re-write and improve MQTT handling](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/900b573d4b286bf03c09eb515b8307f8a6ea5df7) - @RogerSelwyn
- [Remove sub_typing of FIRECOALARM to remove complexity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/d194250999225b681c1088612e7bc88ddc42cb17) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.6](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/2839737cb61d378ebc934af9696d805176914794) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/150d14acfe7edfe04ddead1120313a2c24afb11f) - @actions-user

### 📚 Documentation
- [Add more mqtt detail](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c5ce4cbf7b50c4647007cc164f8a70a3e1012a0b) - @RogerSelwyn
- [Update sensor list](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/29ce753f33a2cc59171f798752380a35605ef77c) - @RogerSelwyn

## v0.1.5 (2023/09/27)
### ✨ Enhancements
- [Add MQTT handling for alert/device/notification/property](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/fe3cc4414e8be60c7a6d13a2d520bca0eef9df82) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4f171945ef779bbef3d62647790a1b566f777ade) - @RogerSelwyn

## v0.1.4 (2023/09/26)
### ✨ Enhancements
- [Add dynamic add/delete of properties and devices](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/82b380fe1aa99bf8562d65f0949be3746d7d5bba) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.4](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/18f6d2022a7f4d4c0d2caa2b672248ed3def9f80) - @RogerSelwyn

## v0.1.3 (2023/09/24)
### 🐛 Fixes
- [Fix error with Attribution](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/09536d62732e5a8e577114197bfd143ee517118a) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to 0.1.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3cf7349d193dfd5565048880d654689310378dba) - @RogerSelwyn

## v0.1.2 (2023/09/24)
### ✨ Enhancements
- [Added support for HA feature removing static attributes from recorder](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/4dd9104fe784613e09aa56a6c512757f196516f2) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/21256f68fd90bfbac69e545b88f85d057d6e05e7) - @RogerSelwyn

## v0.1.1 (2023/09/23)
### ✨ Enhancements
- [Added alarmed devices to propert entity](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a35fb94197a082ce38bed83c24cc2037de54807d) - @RogerSelwyn

### 🐛 Fixes
- [Fix issue with wrong reporting  of property status](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/58f0cbd4b346a49602221d1787dc9eda3cf47cb2) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a640afdbe65ef4b6016b00b4b7e09d3fe26115c0) - @RogerSelwyn

## v0.1.0 (2023/09/23)
### ✨ Enhancements
- [Add support for reauth dialogues](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/12886e5e242d29fdfa22b38651eed272973c17b2) - @RogerSelwyn

### 🔨 Maintenance
- [Bump to v0.1.0](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7f8b31c33af44c1e37364a886a0f35d4728cb1a0) - @RogerSelwyn

## v0.0.5 (2023/09/22)
### ✨ Enhancements
- [Update data immediately when alert received](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/391cfc22c697b1c3c158eeb5cb5c267addc241db) - @RogerSelwyn

### 🐛 Fixes
- [Correct last test date entity name](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/cf9b54bc05c77a90ec51323b8e7975291d2ce034) - @RogerSelwyn

### 🔨 Maintenance
- [Convert literals to constants for stability](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/ab7d17c183ffadbd1273e473121d43ac579e3001) - @RogerSelwyn
- [Bump to 0.0.5](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7e527ab884186dd35bcf64e1afc8722c045b6c8c) - @RogerSelwyn

### 📚 Documentation
- [Update to reflect that alert mqtt message will trigger update](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/0a6260ebcc54c9b18774d2c0f5640aac06704e0e) - @RogerSelwyn

## v0.0.4 (2023/09/22)
### ✨ Enhancements
- [Add replace by date for gateway](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a53e657f051147d9fbe31bee536d39f3f593ddda) - @RogerSelwyn
- [Add more details to mqtt events](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/08b8b8185cebf709e2252090a1550b74d9836402) - @RogerSelwyn
- [Increase number of message types handled from MQTT](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7a33b806064e49217a681c5885bd451084d76e6d) - @RogerSelwyn

### 📚 Documentation
- [Bump to v0.0.4](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/c76b46abb6b2cad7f6dd024bce3585d619f8fe26) - @RogerSelwyn

## v0.0.3 (2023/09/21)
### ✨ Enhancements
- [Added MQTT for events - output to event](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/8fc5abbc81b407b0477cb087be90023ff15a9d34) - @RogerSelwyn
- [Added Replace By as a sensor](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f7a7e2d52e6e48ec17a2402d503d0296f30bb9b3) - @RogerSelwyn
- [Added MQTT config and basic alert subscription](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/7094a3e016f8cb62c95703d19959cfea2c4e10a3) - @RogerSelwyn

### 🐛 Fixes
- [Fix to correct where entity retrieves data from for coordinator update](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a9aba434cf1643d8dd52938afe3f3580d5cf8ea1) - @RogerSelwyn

### 🔨 Maintenance
- [Minor tweaks](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/586a3dda629fe92969352dbbe8203f8abc409bf0) - @RogerSelwyn
- [Add greater detail event raising](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/1a9bbc0b94cc2a09e238b77141b56e9f948c2f07) - @RogerSelwyn
- [Bump to v0.0.3](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/8bebd71cd4d7cb8703c098b43bf5d77910f75f45) - @RogerSelwyn
- [Auto update manifest.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/dc4729ec5f2f453e38e3dc540ac0cd2ae96f3179) - @actions-user

### 📚 Documentation
- [Update CHANGELOG.MD](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/a0165e5e4bfde83317cdcc0547eaf13285b9df37) - @RogerSelwyn
- [Add more detail on config and add MQTT details](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/73f6ee7d3ae0265bf5d9e324c7bcd66dbdb165cf) - @RogerSelwyn

## v0.0.2 (2023/09/20)
### 🔨 Maintenance
- [Update hacs.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/3d02cde6530042c2a7e072301504dfc161957605) - @RogerSelwyn
- [Update hacs.json](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/29f0093fa1ff40d5b9d0ce1927abd04186a69bbf) - @RogerSelwyn
- [Set as cloud_polling](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/29cd85bd3545870c126dc7871de696e7717444e2) - @RogerSelwyn
- [Set last test date sensor as timestamp not date](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/65a704d6ec67f97cc3394b5e670e05317e854cde) - @RogerSelwyn
- [Bump pyhomelink to 0.1.1](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/e0c7b624bc021c373342a906ad2c14f9bd24bb83) - @RogerSelwyn
- [Improve alert handling](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/df5e3b533de1819923f5a8bbe5824520e06e8c89) - @RogerSelwyn
- [Bump to v0.0.2](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/88e9920128ad8e514fc51bf0cedd876ae4d643f7) - @RogerSelwyn
- [Delete .github/workflows/codeql-analysis.yml](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/5d6124245ddada2d053cdd4aea0fae8ab9ce4d8f) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/f41d7f16ac2eb5fa52eb839c0b842d1b14366552) - @actions-user

### 📚 Documentation
- [Update CHANGELOG.MD](https://github.com/RogerSelwyn/AICO_HomeLINK/commit/5278381e6a34fba39b013e39b7804c87d9479dd7) - @RogerSelwyn

## v0.0.1 (2023/09/19)
### Initial Release

- Includes visiblity of alert status of properties and associated devices
