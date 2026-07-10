"""
竞赛信息聚合 - 主入口
调度所有爬虫，合并数据，输出统一 JSON
"""
import glob
import json
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawlers import (
    crawl_saikr,
    crawl_icpc_regional,
    crawl_hackathons,
    crawl_52jingsai,
    crawl_jingrace,
    crawl_dorahacks,
    crawl_devpost,
    get_seed_competitions,
)


def merge_and_deduplicate(all_lists):
    """合并多个数据源并去重"""
    seen = set()
    result = []

    for comp_list in all_lists:
        for comp in comp_list:
            key = comp["title"].strip()
            if key and key not in seen:
                seen.add(key)
                result.append(comp)

    return result


def sort_by_deadline(competitions):
    """按报名截止时间排序（有截止时间的排前面）"""
    def sort_key(item):
        deadline = item.get("registration_deadline") or item.get("contest_start") or "9999-12-31"
        return deadline

    return sorted(competitions, key=sort_key)


def count_categories(competitions):
    """统计分类数量"""
    categories = {}
    for comp in competitions:
        cat = comp.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1
    return categories


def cleanup_old_backups(data_dir, keep_days=30):
    """清理超过 keep_days 天的旧备份文件"""
    pattern = os.path.join(data_dir, "competitions-????-??-??.json")
    files = glob.glob(pattern)
    cutoff = datetime.now().timestamp() - keep_days * 86400
    deleted = 0

    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            date_str = fname.replace("competitions-", "").replace(".json", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date.timestamp() < cutoff:
                os.remove(fpath)
                deleted += 1
        except (ValueError, OSError):
            continue

    return deleted


def main():
    print("=" * 60)
    print("🎯 大学生竞赛信息聚合爬虫启动")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_data = []

    # 0. 种子数据（教育部白名单，确保基础数据）
    print("\n[0/8] 加载教育部白名单种子数据...")
    try:
        seed_data = get_seed_competitions()
        all_data.append(seed_data)
    except Exception as e:
        print(f"种子数据加载异常: {e}")
        all_data.append([])

    # 1. 赛氪（主数据源，最全面）
    print("\n[1/8] 正在爬取赛氪网...")
    try:
        saikr_data = crawl_saikr(max_pages=3)
        all_data.append(saikr_data)
    except Exception as e:
        print(f"赛氪爬取异常: {e}")
        all_data.append([])

    # 2. 我爱竞赛网
    print("\n[2/8] 正在爬取我爱竞赛网...")
    try:
        jingsai52_data = crawl_52jingsai(max_pages=3)
        all_data.append(jingsai52_data)
    except Exception as e:
        print(f"我爱竞赛网爬取异常: {e}")
        all_data.append([])

    # 3. 竞观 Compass
    print("\n[3/8] 正在爬取竞观Compass...")
    try:
        jingrace_data = crawl_jingrace()
        all_data.append(jingrace_data)
    except Exception as e:
        print(f"竞观爬取异常: {e}")
        all_data.append([])

    # 4. ICPC 区域赛
    print("\n[4/8] 正在爬取ICPC区域赛...")
    try:
        icpc_data = crawl_icpc_regional()
        all_data.append(icpc_data)
    except Exception as e:
        print(f"ICPC爬取异常: {e}")
        all_data.append([])

    # 5. Hackalist 全球黑客松
    print("\n[5/8] 正在获取黑客松数据...")
    try:
        hackathon_data = crawl_hackathons()
        all_data.append(hackathon_data)
    except Exception as e:
        print(f"黑客松获取异常: {e}")
        all_data.append([])

    # 6. DoraHacks 全球黑客松
    print("\n[6/8] 正在获取DoraHacks黑客松...")
    try:
        dorahacks_data = crawl_dorahacks()
        all_data.append(dorahacks_data)
    except Exception as e:
        print(f"DoraHacks获取异常: {e}")
        all_data.append([])

    # 7. Devpost 全球黑客松
    print("\n[7/8] 正在获取Devpost黑客松...")
    try:
        devpost_data = crawl_devpost()
        all_data.append(devpost_data)
    except Exception as e:
        print(f"Devpost获取异常: {e}")
        all_data.append([])

    # 合并去重
    merged = merge_and_deduplicate(all_data)
    sorted_list = sort_by_deadline(merged)
    categories = count_categories(sorted_list)

    # 数据质量校验
    valid_count = sum(1 for c in sorted_list if c.get("url"))
    print(f"\n📊 数据质量校验：有效链接 {valid_count}/{len(sorted_list)}")

    if len(sorted_list) < 10:
        print("⚠️  警告：爬取数据量过少，可能爬虫失效！")
        sys.exit(1)

    # 输出结果
    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(sorted_list),
        "categories": categories,
        "competitions": sorted_list
    }

    # 写入 data 目录
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "competitions.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 写入带时间戳的备份
    backup_date = datetime.now().strftime("%Y-%m-%d")
    backup_path = os.path.join(data_dir, f"competitions-{backup_date}.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 清理旧备份
    deleted = cleanup_old_backups(data_dir)

    # 同时复制一份到 frontend 目录，供前端直接读取
    frontend_data = os.path.join(os.path.dirname(__file__), "frontend", "data.json")
    with open(frontend_data, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ 爬取完成！共收集 {len(sorted_list)} 条竞赛信息")
    print("📂 分类统计:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   - {cat}: {count} 条")
    print(f"\n💾 数据已保存到: {output_path}")
    print(f"📦 每日备份: {backup_path}")
    if deleted:
        print(f"🗑️  已清理 {deleted} 个超过 30 天的旧备份")
    print("=" * 60)


if __name__ == "__main__":
    main()
