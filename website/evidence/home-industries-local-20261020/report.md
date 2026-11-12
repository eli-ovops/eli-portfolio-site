# 首页八类行业：本地完成，待用户查看

日期：2026-10-20。唯一执行者：本会话。用户已确认的8类、位置和点击展开形式已实施，中英文同步。候选revision：a1e65a01ed33addd2b34。官网仍按既有已发布版本运行，本轮没有发布、服务器访问、搜索提交、索引请求或外发。

## 内容和范围

首页顺序：现有业务场景 #needs → 新行业板块 #industries → 原代表项目 #work。8类为制造业、电子商务、跨境电商、批发与零售、家具家居与建材、律所与专业服务、品牌与内容工作室、公益机构。默认显示名称和一句场景，点击展开评估范围、相关实践（有依据时）、服务入口和咨询入口。

电子商务不附虚构的电商客户案例；制造和批发项所附的是实际库存流程相关项目，文案说明参考性质；跨境项所附的是品牌出海营销与客服协作，不称平台交易系统开发。其他项依公开字段关联家具展示/库存、律所官网/OA、品牌内容、公益官网。关联项目不证明全行业均有客户，也不承诺设备对接或既有系统集成。

没有新增图片、依赖、行业独立页、价格或效果指标。原首页文案、背景、错层卡片、OA图示、文章轮播和原动效资源保持。关于、服务、文章及原案例正文未改。新CSS仅作用于 .industry-*，无毛玻璃；新脚本复用现有PortfolioMotion的0.3秒展开/收起，无JS时使用原生details。

## 文件

新增 content/industry-scenarios.json、scripts/industries.py、assets/industry-scenarios.css、assets/industry-scenarios.js。

修改 scripts/pages.py、scripts/components.py、templates/home.html；content/page-updates.json仅更新两个首页的内容指纹和真实日期；site.yaml仅登记本地待审候选，未修改线上revision。dist由现有标准构建生成。

before/保存涉及的既有源码、契约、日期账本和双语首页快照；before-hashes.json保存296页与30个既有CSS/JS哈希。新建报告、检查原件和截图用于审阅与回退，没有可自动删除的无用中间文件。

## 验证

- npm run build -- --record-lastmod 2026-10-20：通过，296 HTML、38项目。日期账本只变两个首页，其他292个可索引页内容指纹不变；404不在日期账本。
- node --check assets/industry-scenarios.js：通过。
- python3 scripts/check.py：296页HTTP、内部链接、锚点、单H1、原始客户素材隔离通过。此历史脚本输出的date固定为2026-10-06，不当成本轮日期；本轮运行日期与结果由receipt记录。
- python3 scripts/check_seo.py --output evidence/home-industries-local-20261020/seo-checks.json：通过，296独立标题/摘要、204文章详情、294地图URL、双语规范链接与结构化信息。没有提交地图。
- static-scope-checks.json：两种语言8项顺序正确，7项有真实相关项目、1项无案例，8项都有服务与咨询入口。英文新板块无中文漏翻。30个原CSS/JS字节未变。
- CUA真实浏览器：桌面1280px查看列表与展开；360px中文、390px英文各8项逐一展开/收起，均无页面横向溢出，确认44px咨询链接高度；中文Enter键可展开。
- 首页EN切换保持 #industries，进入对应英文首页；英文行业入口进入 /en/about.html#contact，二维码可见，联系页切回中文保留 #contact；中文无案例行业同样能进入 /about.html#contact。
- 关联P10实际进入案例，返回按钮实际回到首页 #work 并带 project=p10，沿用原首页案例返回逻辑，未新增回到展开行业的逻辑。

手机为浏览器模拟，不是真机。没有发送咨询、点击拨号或外发消息；以上均是QA，不作自然流量/咨询/成交。

## 检查中的工具问题

一条中文Python stdin在解析阶段报编码错误，未创建文件，按LOCAL_BLOCKERS既有方法改ASCII脚本与apply_patch；未改系统语言或环境。一次旧浏览器标签返回操作超时并丢失控制绑定，重新读取实际标签状态，同一浏览器新建本地标签完成手机、语言和案例返回检查；未绕过安全挑战或换网络。原卡片与网站功能没有为工具问题而改动。

本地预览服务沿用127.0.0.1:4178，仅读取dist，恢复了此前未启动的预览进程。没有生产服务操作。
