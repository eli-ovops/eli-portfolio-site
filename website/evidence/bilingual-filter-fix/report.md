# 双语筛选差异修复 — 2026-10-07

根因：英文版实施时，app.js中文分支const allCategory自引用触发ReferenceError，导致中文分类/搜索栏保持hidden，整个app.js初始化中止。此前只核对HTML分类存在，没有验证中文运行态，错误回报了两版相同。

修复：仅将默认中文分类值还原为字符串“全部”。英文分支保留All。分类、案例数据、样式没有变更。新增scripts/check_app_locales.cjs运行两个语言启动分支，防止语法检查遗漏运行时TDZ。两个分支均通过。

build84页、静态检查84页、英文42页本地化检查均通过。浏览器中英文搜索库存/inventory均2条，客户项目/Client work均5条，全部/All均38条。公网中文分类栏已实际显示，修复app.js公网哈希与构建相同，health版本核对通过。

release20261007-134331，包SHA909a0fefc303db62ec3020aafc0776822b6b5eb2f2f487cfceafbab6f0d2a5ae。只app.js及health与旧121文件发布包不同，其他文件逐一核对相同。原子切换独立portfolio/public，不改Nginx/重启ERP。旧版20261007-133421保留作恢复证据，但该版中文初始化错误不可视为已验收。

本目录app.before.js、browser-checks.json、包、文件哈希、release.json、deploy.py和public-chinese.jpg保留用于审查与回退。源码新增检查脚本；README已更新发布记录。未清理其他文件、媒体或备份。
