# Awesome LiteMonitor Plugins

> 社区维护的 [LiteMonitor++](https://github.com/mojingjing-git/LiteMonitorPlus) 插件索引与生态资源清单（**非官方**）。

## 这是什么

LiteMonitor++ 的插件仓库。**每个插件一个目录**，目录下的 `README.md` 就是插件介绍页（GitHub 会自动渲染在目录页顶部），`plugin.json` 是插件本体。

LiteMonitor++ 软件内的「设置 → 插件市场」从这里拉取索引，一键安装。

## 插件清单

见 **[PLUGINS.md](./PLUGINS.md)** —— 由 CI 自动生成，请勿手工编辑。

## 目录结构

```
plugins/
  <插件 id>/
    plugin.json     插件本体（机器可读，声明去哪取数、怎么提取、怎么显示）
    README.md       插件介绍（人可读，渲染在目录页上）
    verified        审核标记（可选空文件，存在即表示已实机验证）
```

## 贡献一个插件

1. Fork 本仓库
2. 在 `plugins/<你的插件 id>/` 下放入 `plugin.json` 与 `README.md`
3. 目录名必须与 `plugin.json` 里的 `id` **完全一致**
4. 本地跑 `python3 scripts/gen_index.py --check` 确认通过
5. 提 PR —— CI 会自动校验，通过后由审核 Agent 实机验证并打标

### 命名规则

| 规则 | 说明 |
|---|---|
| `id` 只能包含 `A-Za-z0-9-_`，最长 64 字符 | 目录名与落盘文件名都基于它 |
| `id` 不能与内置插件重名 | 内置插件清单见 `scripts/gen_index.py` 的 `BUILTIN_IDS` |
| 目录名必须 == `id` | CI 强制校验 |
| **`id` 一经合并即不可更改** | 它是用户的安装主键，改 id 等于换插件 |

> 目录名一旦随插件发布并被用户安装，改名会导致老用户配置失效。

### `plugin.json` 必填字段

| 字段 | 说明 |
|---|---|
| `id` | 唯一标识，见上方命名规则 |
| `meta.name` | 中文名 |
| `meta.description` | 中文简介（软件市场列表显示的就是它） |
| `meta.author` | **真实作者**（GitHub 用户名最佳）—— 填 `User` / `Codex` 这类占位符会让用户无法判断该不该信任 |
| `meta.version` | 版本号 |

强烈建议同时填写 `meta.name_en` / `meta.description_en`，以及每个 `outputs[]` 的 `label_en` / `short_label_en` —— **英文界面下显示的就是这些字段**，缺失会回退中文。

### `README.md` 必填小节

| 小节 | 是否必填 |
|---|---|
| `## 功能说明` | 必填 |
| `## 输出项` | 必填 |
| `## 注意事项` | 必填（**踩坑提示是本仓库的核心价值**） |
| `## 配置项` | 本插件有 `inputs` 时必填 |
| `## 使用说明` | 建议 |

「配置项」「输出项」两张表由 `scripts/init_readme.py` 从 `plugin.json` 自动生成（`<!-- AUTO:xxx -->` 标记之间），改完插件配置后重跑脚本即可刷新：

```bash
python3 scripts/init_readme.py          # 生成缺失的 README，刷新已有 README 的表格
python3 scripts/init_readme.py --force  # 强制重建（会丢弃手工修改）
```

### 双语字段

`scripts/fix_i18n.py` 可以自动补全一部分缺失的 `_en` 字段（不含 CJK 的文案，如缩写、emoji、符号可直接复用）：

```bash
python3 scripts/fix_i18n.py           # 只检查，报告缺口
python3 scripts/fix_i18n.py --apply   # 补全可自动推导的部分
```

含中文的文案无法自动翻译，需要人工填写。

## 审核流程

插件的 PR **不会自动合并**：

| 环节 | 谁做 | 产出 |
|---|---|---|
| 格式校验 | CI（`validate` job） | PR 变绿/变红 + 校验报告 artifact |
| **内容审核** | **审核 Agent** | 审核结论 + `plugins/<id>/verified` 标记文件 |
| 合并与发布 | 合并 PR → CI `publish-index` | `index.json` 更新，插件上架 |

**审核 Agent 的检查清单**：

- [ ] `plugin.json` 字段完整，`id` 与目录名一致
- [ ] 插件请求的域名合理（无可疑 / 广告 / 数据回传域名）
- [ ] 不索取不必要的凭据（只要求该插件确实需要的）
- [ ] **实机安装运行**，确认监控项有正常数值（不是 `[ERROR]` / `[EMPTY]`）
- [ ] README 的「注意事项」写清了已知的限制与坑
- [ ] `meta.author` 是真实作者

审核通过后，提交 `plugins/<id>/verified` 空文件，PR 合并后 CI 会自动把它写进索引。

## 插件安全说明

插件是**纯声明式 JSON 配置** —— 只声明「去哪取数、怎么提取、怎么显示」，**不具备执行第三方脚本或代码的能力**。

但插件会**按配置发起网络请求**，可能把你的 IP 或填写的 API Key 发送给对应服务。例如填写了某个云服务的 API Key 后，插件会把它发往该服务的接口。请只安装可信来源的插件，并留意插件 README 里说明的请求域名。

## 本地开发

```bash
git clone https://github.com/mojingjing-git/awesome-litemonitor-plugins.git
cd awesome-litemonitor-plugins

python3 scripts/gen_index.py --check    # 校验（不改产物）
python3 scripts/gen_index.py             # 校验 + 生成 index.json / PLUGINS.md
```

需要 Python 3.8+，无第三方依赖。

## 免责声明

本仓库与 LiteMonitor++ 原作者 Diorser 无关联，为社区维护的非官方项目。插件由社区贡献，质量参差不齐，**请自行判断是否信任**。安装插件等同于同意它按配置访问你填写的服务。

## 许可证

仓库内容采用 [MIT](LICENSE) 协议。各插件可能采用不同许可，由各自作者在 `meta` 中声明。
