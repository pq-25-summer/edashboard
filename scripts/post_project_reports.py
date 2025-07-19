#!/usr/bin/env python3
"""
批量提交项目报告到GitHub Issue

将每个项目的详细状态报告提交到指定的GitHub Issue中。
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import subprocess
import time


def post_project_report(issue_number: int, report_file: str) -> bool:
    """提交单个项目报告到GitHub Issue"""
    try:
        print(f"📤 提交报告: {report_file}")
        
        # 使用gh命令提交评论
        result = subprocess.run(
            ['gh', 'issue', 'comment', str(issue_number), '--body-file', report_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ 成功提交: {report_file}")
            return True
        else:
            print(f"❌ 提交失败: {report_file}")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ 提交超时: {report_file}")
        return False
    except Exception as e:
        print(f"❌ 提交异常: {report_file} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="批量提交项目报告到GitHub Issue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python post_project_reports.py --issue 1
  python post_project_reports.py --issue 1 --pattern "project_report_*.md"
        """
    )
    
    parser.add_argument(
        '--issue',
        type=int,
        required=True,
        help='GitHub Issue编号'
    )
    
    parser.add_argument(
        '--pattern',
        default='project_report_*.md',
        help='报告文件匹配模式'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=2,
        help='提交间隔时间（秒）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际提交'
    )
    
    args = parser.parse_args()
    
    # 查找所有报告文件
    report_files = glob.glob(args.pattern)
    report_files.sort()  # 按文件名排序
    
    if not report_files:
        print(f"❌ 未找到匹配模式 '{args.pattern}' 的报告文件")
        sys.exit(1)
    
    print(f"📋 找到 {len(report_files)} 个报告文件")
    print("=" * 50)
    
    if args.dry_run:
        print("🔍 预览模式 - 将提交以下报告:")
        for report_file in report_files:
            print(f"  - {report_file}")
        return
    
    # 提交每个报告
    success_count = 0
    total_count = len(report_files)
    
    for i, report_file in enumerate(report_files, 1):
        print(f"\n[{i}/{total_count}] 处理: {report_file}")
        
        if post_project_report(args.issue, report_file):
            success_count += 1
        
        # 添加延迟，避免API限制
        if i < total_count:
            print(f"⏳ 等待 {args.delay} 秒...")
            time.sleep(args.delay)
    
    # 打印总结
    print("\n" + "=" * 50)
    print("📊 提交总结:")
    print(f"- 总报告数: {total_count}")
    print(f"- 成功提交: {success_count}")
    print(f"- 失败数量: {total_count - success_count}")
    print(f"- 成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
    
    if success_count == total_count:
        print("🎉 所有报告提交成功！")
        sys.exit(0)
    else:
        print("⚠️  部分报告提交失败")
        sys.exit(1)


if __name__ == '__main__':
    main() 