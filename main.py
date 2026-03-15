#!/usr/bin/env python3
"""
Railway 部署版本 - 个股研究数据库
简化版：使用示例数据，适合云端部署
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# ============== 示例数据（避免依赖本地大文件） ==============

SAMPLE_DATA = {
    "stats": {
        "total_stocks": 1502,
        "total_mentions": 4610,
        "total_companies": 1502,
        "total_articles": 731,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    },
    "top_10": [
        {"rank": 1, "code": "300024", "name": "机器人", "mentions": 68, "with_target": 2, "concepts": ["机器人", "AI", "自动化"]},
        {"rank": 2, "code": "300308", "name": "中际旭创", "mentions": 27, "with_target": 1, "concepts": ["CPO", "光模块", "AI"]},
        {"rank": 3, "code": "300502", "name": "新易盛", "mentions": 25, "with_target": 1, "concepts": ["CPO", "光模块"]},
        {"rank": 4, "code": "603986", "name": "兆易创新", "mentions": 23, "with_target": 0, "concepts": ["半导体", "存储芯片"]},
        {"rank": 5, "code": "300394", "name": "天孚通信", "mentions": 23, "with_target": 1, "concepts": ["CPO", "光通信"]},
        {"rank": 6, "code": "300274", "name": "阳光电源", "mentions": 22, "with_target": 2, "concepts": ["光伏", "储能"]},
        {"rank": 7, "code": "688516", "name": "奥特维", "mentions": 22, "with_target": 0, "concepts": ["光伏", "半导体"]},
        {"rank": 8, "code": "300475", "name": "香农芯创", "mentions": 21, "with_target": 0, "concepts": ["半导体", "分销"]},
        {"rank": 9, "code": "002156", "name": "通富微电", "mentions": 21, "with_target": 1, "concepts": ["半导体", "封测"]},
        {"rank": 10, "code": "001309", "name": "德明利", "mentions": 20, "with_target": 0, "concepts": ["存储", "芯片"]}
    ],
    "industry_distribution": {
        "沪市主板": 456,
        "深市主板": 415,
        "创业板": 405,
        "科创板": 226
    },
    "stocks": [
        {"code": "300024", "name": "机器人", "industry": "创业板", "mention_count": 68, "with_target": 2, "concepts": ["机器人", "AI", "自动化"]},
        {"code": "300308", "name": "中际旭创", "industry": "创业板", "mention_count": 27, "with_target": 1, "concepts": ["CPO", "光模块"]},
        {"code": "300502", "name": "新易盛", "industry": "创业板", "mention_count": 25, "with_target": 1, "concepts": ["CPO", "光模块"]},
        {"code": "603986", "name": "兆易创新", "industry": "沪市主板", "mention_count": 23, "with_target": 0, "concepts": ["半导体", "存储芯片"]},
        {"code": "300394", "name": "天孚通信", "industry": "创业板", "mention_count": 23, "with_target": 1, "concepts": ["CPO", "光通信"]},
    ]
}

# ============== HTML 模板 ==============

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个股研究数据库 - 仪表板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <h1 class="text-xl font-bold text-gray-900">📊 个股研究数据库</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/" class="text-blue-600 font-medium">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">股票池</div>
                <div class="text-3xl font-bold text-blue-600 mt-2" id="total-stocks">{{ stats.total_stocks }}</div>
                <div class="text-xs text-gray-500 mt-1">只股票</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">有效提及</div>
                <div class="text-3xl font-bold text-green-600 mt-2" id="total-mentions">{{ stats.total_mentions }}</div>
                <div class="text-xs text-gray-500 mt-1">条</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">覆盖公司</div>
                <div class="text-3xl font-bold text-purple-600 mt-2" id="total-companies">{{ stats.total_companies }}</div>
                <div class="text-xs text-gray-500 mt-1">家</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">文章数量</div>
                <div class="text-3xl font-bold text-orange-600 mt-2" id="total-articles">{{ stats.total_articles }}</div>
                <div class="text-xs text-gray-500 mt-1">篇</div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow mb-8">
            <div class="px-6 py-4 border-b">
                <h2 class="text-lg font-semibold text-gray-900">📈 有效提及 Top 10</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">排名</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">提及次数</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">目标价</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">概念标签</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {% for stock in top_10 %}
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stock.rank }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-blue-600 font-medium">{{ stock.name }} ({{ stock.code }})</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stock.mentions }}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm {{ 'text-green-600' if stock.with_target > 0 else 'text-gray-400' }}">
                                {{ '✅' if stock.with_target > 0 else '-' }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex flex-wrap gap-1">
                                    {% for concept in stock.concepts %}
                                    <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{{ concept }}</span>
                                    {% endfor %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b">
                <h2 class="text-lg font-semibold text-gray-900">🏢 行业分布</h2>
            </div>
            <div class="p-6">
                <canvas id="industry-chart" height="100"></canvas>
            </div>
        </div>
    </main>

    <script>
        const industryData = {{ industry_distribution | tojson }};
        const ctx = document.getElementById('industry-chart').getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(industryData),
                datasets: [{
                    label: '股票数量',
                    data: Object.values(industryData),
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>
"""

STOCKS_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票列表 - 个股研究数据库</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <h1 class="text-xl font-bold text-gray-900">📊 个股研究数据库</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/" class="text-gray-600 hover:text-gray-900">仪表板</a>
                    <a href="/stocks" class="text-blue-600 font-medium">股票列表</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">代码</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名称</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">板块</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">提及次数</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">概念标签</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {% for stock in stocks %}
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{{ stock.code }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-blue-600 font-medium">{{ stock.name }}</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ stock.industry }}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stock.mention_count }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex flex-wrap gap-1">
                                    {% for concept in stock.concepts %}
                                    <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">{{ concept }}</span>
                                    {% endfor %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
</body>
</html>
"""

# ============== 路由 ==============

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE, **SAMPLE_DATA)

@app.route('/stocks')
def stocks_list():
    return render_template_string(STOCKS_TEMPLATE, stocks=SAMPLE_DATA["stocks"])

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(SAMPLE_DATA)

@app.route('/api/stocks')
def api_stocks():
    return jsonify({
        "total": len(SAMPLE_DATA["stocks"]),
        "stocks": SAMPLE_DATA["stocks"]
    })

# ============== 启动 ==============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
