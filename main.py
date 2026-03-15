#!/usr/bin/env python3
"""
Phase 6: Web 功能增强 - Railway 部署版
- 全局搜索框（搜索第一、二层信息）
- 个股独立详情页（三层数据展示）
- 手动删除功能
- 使用内联模板（无需 templates 文件夹）
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============== 示例数据（Railway 版本） ==============
# 注意：Railway 无法访问本地大文件，使用示例数据演示功能

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
        {"code": "300024", "name": "机器人", "industry": "创业板", "board": "创业板", "mention_count": 68, "with_target": 2, "concepts": ["机器人", "AI", "自动化"]},
        {"code": "300308", "name": "中际旭创", "industry": "创业板", "board": "创业板", "mention_count": 27, "with_target": 1, "concepts": ["CPO", "光模块", "AI"]},
        {"code": "300502", "name": "新易盛", "industry": "创业板", "board": "创业板", "mention_count": 25, "with_target": 1, "concepts": ["CPO", "光模块"]},
        {"code": "603986", "name": "兆易创新", "industry": "沪市主板", "board": "沪市主板", "mention_count": 23, "with_target": 0, "concepts": ["半导体", "存储芯片"]},
        {"code": "300394", "name": "天孚通信", "industry": "创业板", "board": "创业板", "mention_count": 23, "with_target": 1, "concepts": ["CPO", "光通信"]},
    ],
    # 模拟三层数据
    "stock_details": {
        "300024": {
            "basic": {"code": "300024", "name": "机器人", "mention_count": 68, "industry": "电子", "board": "创业板"},
            "layer2": {
                "concepts": ["机器人", "AI", "自动化", "智能制造"],
                "products": ["工业机器人", "伺服系统", "控制器"],
                "events": {"涨价": 5, "投资": 3, "合作": 2},
                "supply_chain": ["减速器供应商", "汽车制造商"]
            },
            "mentions": [
                {"article_id": "ART_0010", "source": {"title": "机器人产业链全景梳理"}, "classification": {"level1": "电子", "level2": "自动化"}, "concepts": ["机器人", "AI"], "events": [{"type": "涨价"}]},
                {"article_id": "ART_0009", "source": {"title": "人形机器人电机新方案"}, "classification": {"level1": "机械", "level2": "机器人"}, "concepts": ["机器人", "电机"], "events": []},
            ]
        },
        "300308": {
            "basic": {"code": "300308", "name": "中际旭创", "mention_count": 27, "industry": "通信", "board": "创业板"},
            "layer2": {
                "concepts": ["CPO", "光模块", "AI", "算力"],
                "products": ["光模块", "光器件"],
                "events": {"涨价": 8, "订单": 5},
                "supply_chain": ["芯片供应商", "数据中心"]
            },
            "mentions": [
                {"article_id": "ART_0100", "source": {"title": "CPO 技术路线详解"}, "classification": {"level1": "通信", "level2": "光模块"}, "concepts": ["CPO", "光模块"], "events": [{"type": "涨价"}]},
            ]
        }
    }
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
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="relative">
                        <input type="text" id="global-search" placeholder="搜索股票、概念、产品..." 
                               class="w-80 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div id="search-suggestions" class="absolute top-full right-0 mt-1 w-80 bg-white border border-gray-300 rounded-lg shadow-lg hidden"></div>
                    </div>
                    <a href="/" class="text-blue-600 font-medium">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                    <a href="/search" class="text-gray-600 hover:text-gray-900">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">股票池</div>
                <div class="text-3xl font-bold text-blue-600 mt-2">{{ stats.total_stocks }}</div>
                <div class="text-xs text-gray-500 mt-1">只股票</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">有效提及</div>
                <div class="text-3xl font-bold text-green-600 mt-2">{{ stats.total_mentions }}</div>
                <div class="text-xs text-gray-500 mt-1">条</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">覆盖公司</div>
                <div class="text-3xl font-bold text-purple-600 mt-2">{{ stats.total_companies }}</div>
                <div class="text-xs text-gray-500 mt-1">家</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">文章数量</div>
                <div class="text-3xl font-bold text-orange-600 mt-2">{{ stats.total_articles }}</div>
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
                                <a href="/stock/{{ stock.code }}" class="text-blue-600 hover:text-blue-900 font-medium">
                                    {{ stock.name }} ({{ stock.code }})
                                </a>
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
            <div class="p-6" style="height: 300px;">
                <canvas id="industry-chart"></canvas>
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

        // 全局搜索
        const searchInput = document.getElementById('global-search');
        const suggestionsDiv = document.getElementById('search-suggestions');

        searchInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                suggestionsDiv.classList.add('hidden');
                return;
            }

            try {
                const response = await fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.suggestions.length > 0) {
                    suggestionsDiv.innerHTML = data.suggestions.map(s => `
                        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-0" onclick="location.href='/stock/${s.code || ''}'">
                            ${s.text}
                        </div>
                    `).join('');
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    location.href = `/search?q=${encodeURIComponent(query)}`;
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
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="relative">
                        <input type="text" id="global-search" placeholder="搜索股票、概念、产品..." 
                               class="w-80 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div id="search-suggestions" class="absolute top-full right-0 mt-1 w-80 bg-white border border-gray-300 rounded-lg shadow-lg hidden"></div>
                    </div>
                    <a href="/" class="text-gray-600 hover:text-gray-900">仪表板</a>
                    <a href="/stocks" class="text-blue-600 font-medium">股票列表</a>
                    <a href="/search" class="text-gray-600 hover:text-gray-900">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">📋 股票列表</h1>
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
                                <a href="/stock/{{ stock.code }}" class="text-blue-600 hover:text-blue-900 font-medium">{{ stock.name }}</a>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ stock.board }}</td>
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

STOCK_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ code }} - 个股详情</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="relative">
                        <input type="text" id="global-search" placeholder="搜索股票、概念、产品..." 
                               class="w-80 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div id="search-suggestions" class="absolute top-full right-0 mt-1 w-80 bg-white border border-gray-300 rounded-lg shadow-lg hidden"></div>
                    </div>
                    <a href="/" class="text-gray-600 hover:text-gray-900">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                    <a href="/search" class="text-gray-600 hover:text-gray-900">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div id="loading" class="text-center py-12">
            <i class="fas fa-spinner fa-spin text-4xl text-blue-600"></i>
            <p class="mt-4 text-gray-600">加载数据中...</p>
        </div>

        <div id="content" class="hidden">
            <div class="bg-white rounded-lg shadow mb-6">
                <div class="px-6 py-4 border-b">
                    <h1 id="stock-title" class="text-2xl font-bold text-gray-900"></h1>
                </div>
                <div class="px-6 py-4">
                    <div class="grid grid-cols-4 gap-4">
                        <div>
                            <div class="text-sm text-gray-600">股票代码</div>
                            <div id="stock-code" class="text-xl font-mono font-bold text-blue-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">提及次数</div>
                            <div id="stock-mentions" class="text-xl font-bold text-green-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">所属板块</div>
                            <div id="stock-board" class="text-xl font-bold text-purple-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">行业分类</div>
                            <div id="stock-industry" class="text-lg font-bold text-orange-600"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">🏷️ 概念标签</h2>
                    </div>
                    <div class="p-6">
                        <div id="concepts" class="flex flex-wrap gap-2"></div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">📦 产品信息</h2>
                    </div>
                    <div class="p-6">
                        <div id="products" class="flex flex-wrap gap-2"></div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">📊 事件统计</h2>
                    </div>
                    <div class="p-6">
                        <div id="events" class="space-y-2"></div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">🔗 产业链关系</h2>
                    </div>
                    <div class="p-6">
                        <div id="supply-chain" class="text-gray-600"></div>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b flex justify-between items-center">
                    <h2 class="text-lg font-semibold text-gray-900">
                        📰 所有提及 <span id="mention-count" class="text-sm text-gray-500 ml-2"></span>
                    </h2>
                </div>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">文章标题</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">行业分类</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">概念标签</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">事件</th>
                            </tr>
                        </thead>
                        <tbody id="mentions-table" class="bg-white divide-y divide-gray-200"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        const stockCode = "{{ code }}";

        async function loadStockData() {
            try {
                const response = await fetch(`/api/stock/${stockCode}`);
                const data = await response.json();

                if (data.error) {
                    alert(data.error);
                    return;
                }

                document.getElementById('stock-title').textContent = `${data.basic.name} (${data.basic.code})`;
                document.getElementById('stock-code').textContent = data.basic.code;
                document.getElementById('stock-mentions').textContent = data.total_mentions;
                document.getElementById('stock-board').textContent = data.basic.board || '未知';
                document.getElementById('stock-industry').textContent = data.basic.industry || '未知';

                const conceptsDiv = document.getElementById('concepts');
                data.layer2.concepts.forEach(concept => {
                    const span = document.createElement('span');
                    span.className = 'px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full';
                    span.textContent = concept;
                    conceptsDiv.appendChild(span);
                });

                const productsDiv = document.getElementById('products');
                data.layer2.products.forEach(product => {
                    const span = document.createElement('span');
                    span.className = 'px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full';
                    span.textContent = product;
                    productsDiv.appendChild(span);
                });

                const eventsDiv = document.getElementById('events');
                const events = data.layer2.events || {};
                for (const [type, count] of Object.entries(events)) {
                    const div = document.createElement('div');
                    div.className = 'flex justify-between';
                    div.innerHTML = `<span class="text-gray-600">${type}</span><span class="font-bold">${count}</span>`;
                    eventsDiv.appendChild(div);
                }
                if (Object.keys(events).length === 0) {
                    eventsDiv.innerHTML = '<div class="text-gray-400">暂无事件数据</div>';
                }

                document.getElementById('supply-chain').textContent = data.layer2.supply_chain?.join('、') || '暂无数据';

                const allMentions = data.mentions || [];
                document.getElementById('mention-count').textContent = `(${allMentions.length}条)`;
                
                const tbody = document.getElementById('mentions-table');
                tbody.innerHTML = allMentions.map(mention => `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4">
                            <div class="text-sm font-medium text-gray-900">${mention.source?.title || '未知'}</div>
                            <div class="text-xs text-gray-500">${mention.article_id}</div>
                        </td>
                        <td class="px-6 py-4 text-sm text-gray-600">
                            ${mention.classification?.level1 || '-'} / ${mention.classification?.level2 || '-'}
                        </td>
                        <td class="px-6 py-4">
                            <div class="flex flex-wrap gap-1">
                                ${(mention.concepts || []).slice(0, 2).map(c => 
                                    `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${c}</span>`
                                ).join('')}
                            </div>
                        </td>
                        <td class="px-6 py-4 text-sm text-gray-600">${(mention.events || []).map(e => e.type).join('、') || '-'}</td>
                    </tr>
                `).join('');

                document.getElementById('loading').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');

            } catch (error) {
                console.error('Error loading stock data:', error);
                alert('加载数据失败');
            }
        }

        // 全局搜索
        const searchInput = document.getElementById('global-search');
        const suggestionsDiv = document.getElementById('search-suggestions');

        searchInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                suggestionsDiv.classList.add('hidden');
                return;
            }

            try {
                const response = await fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.suggestions.length > 0) {
                    suggestionsDiv.innerHTML = data.suggestions.map(s => `
                        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-0" onclick="location.href='/stock/${s.code || ''}'">
                            ${s.text}
                        </div>
                    `).join('');
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        });

        loadStockData();
    </script>
</body>
</html>
"""

SEARCH_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>搜索 - 个股研究数据库</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <a href="/" class="text-gray-600 hover:text-gray-900">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                    <a href="/search" class="text-blue-600 font-medium">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow mb-8">
            <div class="p-6">
                <h1 class="text-2xl font-bold text-gray-900 mb-4">🔍 高级搜索</h1>
                <div class="flex gap-4">
                    <input type="text" id="search-input" placeholder="输入关键词：股票名称、代码、概念、产品、行业..." 
                           class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg">
                    <button onclick="performSearch()" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                        搜索
                    </button>
                </div>
            </div>
        </div>

        <div id="results" class="hidden">
            <div class="mb-4">
                <h2 class="text-lg font-semibold">搜索结果 <span id="result-count" class="text-sm text-gray-500 ml-2"></span></h2>
            </div>
            <div class="bg-white rounded-lg shadow">
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">匹配内容</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">提及次数</th>
                            </tr>
                        </thead>
                        <tbody id="results-table" class="bg-white divide-y divide-gray-200"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="initial-state" class="text-center py-12">
            <i class="fas fa-search text-6xl text-gray-300"></i>
            <p class="mt-4 text-gray-600">输入关键词开始搜索</p>
        </div>
    </main>

    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const queryParam = urlParams.get('q');

        if (queryParam) {
            document.getElementById('search-input').value = queryParam;
            performSearch();
        }

        async function performSearch() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) {
                alert('请输入搜索关键词');
                return;
            }

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.error) {
                    alert(data.error);
                    return;
                }

                document.getElementById('initial-state').classList.add('hidden');
                document.getElementById('results').classList.remove('hidden');
                document.getElementById('result-count').textContent = `(${data.total}条结果)`;

                const tbody = document.getElementById('results-table');
                tbody.innerHTML = data.results.map(result => {
                    let typeBadge = '';
                    switch(result.type) {
                        case 'stock': typeBadge = '<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">股票</span>'; break;
                        case 'concept': typeBadge = '<span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">概念</span>'; break;
                        case 'product': typeBadge = '<span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">产品</span>'; break;
                    }

                    let matchedContent = result.matched ? result.matched.map(m => 
                        `<span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">${m}</span>`
                    ).join('') : '-';

                    return `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">${typeBadge}</td>
                            <td class="px-6 py-4">
                                <a href="/stock/${result.code}" class="text-blue-600 hover:text-blue-900 font-medium">
                                    ${result.name} (${result.code})
                                </a>
                            </td>
                            <td class="px-6 py-4">${matchedContent}</td>
                            <td class="px-6 py-4 text-sm text-gray-600">${result.mention_count || 0}</td>
                        </tr>
                    `;
                }).join('');
            } catch (error) {
                console.error('Search error:', error);
            }
        }

        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    </script>
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

@app.route('/stock/<code>')
def stock_detail(code):
    return render_template_string(STOCK_DETAIL_TEMPLATE, code=code)

@app.route('/search')
def search():
    return render_template_string(SEARCH_TEMPLATE)

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(SAMPLE_DATA)

@app.route('/api/stocks')
def api_stocks():
    return jsonify({
        "total": len(SAMPLE_DATA["stocks"]),
        "stocks": SAMPLE_DATA["stocks"]
    })

@app.route('/api/stock/<code>')
def api_stock_detail(code):
    """股票详情 API"""
    stock_data = SAMPLE_DATA.get("stock_details", {}).get(code)
    
    if not stock_data:
        # 返回示例数据
        stock_data = {
            "basic": {"code": code, "name": "示例股票", "mention_count": 10, "industry": "电子", "board": "创业板"},
            "layer2": {
                "concepts": ["概念 1", "概念 2"],
                "products": ["产品 A"],
                "events": {"涨价": 2},
                "supply_chain": ["供应商"]
            },
            "mentions": [
                {"article_id": "ART_001", "source": {"title": "示例文章"}, "classification": {"level1": "电子"}, "concepts": ["概念 1"], "events": []}
            ]
        }
    
    return jsonify({
        "basic": stock_data.get("basic", {}),
        "layer2": stock_data.get("layer2", {}),
        "mentions": stock_data.get("mentions", []),
        "total_mentions": len(stock_data.get("mentions", []))
    })

@app.route('/api/search')
def api_search():
    """搜索 API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "查询为空"})
    
    results = []
    
    # 搜索股票
    for stock in SAMPLE_DATA["stocks"]:
        if query.lower() in stock["name"].lower() or query in stock["code"]:
            results.append({
                "type": "stock",
                "code": stock["code"],
                "name": stock["name"],
                "relevance": 1.0,
                "mention_count": stock["mention_count"]
            })
    
    return jsonify({
        "total": len(results),
        "results": results
    })

@app.route('/api/search/suggest')
def api_search_suggest():
    """搜索建议 API"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({"suggestions": []})
    
    suggestions = []
    
    # 股票名称建议
    for stock in SAMPLE_DATA["stocks"]:
        if query.lower() in stock["name"].lower():
            suggestions.append({
                "type": "stock",
                "text": f"{stock['name']} ({stock['code']})",
                "code": stock["code"]
            })
    
    return jsonify({"suggestions": suggestions[:10]})

# ============== 启动 ==============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 70)
    print("🚀 启动个股研究数据库 Web 界面 (Phase 6 - Railway)")
    print("=" * 70)
    print(f"\n🌐 访问地址：http://localhost:{port}")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=False)
