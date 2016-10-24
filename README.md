# これはなに

## sqlite3_transact_exp.py

Pythonのsqlite3でSELECT -> UPDATEを1トランザクションで行う実験。

自動コミットモード、DEFERRED, IMMEDIATE, EXCLUSIVEの挙動を比較できるようにした。

```
$ ./sqlite3_transact_exp.py -i e
2016-10-24 22:49:43,943 Start Running
2016-10-24 22:49:43,943 module_version: 2.6.0
2016-10-24 22:49:43,943 sqlite3_version: 3.15.0
2016-10-24 22:49:44,176 result: 100
2016-10-24 22:49:44,177 Finished Running
```

## sqlite3_sierra_exp.py

本プログラム作成時にmacOS Sierraのlibsqlite3に深刻な問題が存在するらしきことが分かったため、それを検証するために作ったコード。詳細は以下を参照のこと。

http://qiita.com/amedama/items/358b5ee76e5f5db0a486

## License

```
Copyright 2016 Daisuke Miyakawa

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
