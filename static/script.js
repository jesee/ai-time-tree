document.addEventListener('DOMContentLoaded', function() {
    const timeline = document.getElementById('timeline');
    const loadTrigger = document.getElementById('load-trigger');
    const loadingIndicator = document.getElementById('loading-indicator');

    let currentPage = 0;
    const articlesPerPage = 10;
    let isLoading = false;
    let allArticlesLoaded = false;

    // 格式化日期函数 (最终健壮版)
    function formatDate(dateString) {
        try {
            // 将日期字符串中的空格替换为 'T'，使其成为严格的 ISO 8601 格式，
            // 这是在所有浏览器中最可靠的解析方式。
            const isoString = dateString.replace(' ', 'T');
            const date = new Date(isoString);

            // 检查日期对象是否有效
            if (isNaN(date.getTime())) {
                console.error("解析为无效日期:", dateString);
                return "日期无效";
            }

            const year = date.getFullYear();
            // getMonth() 返回 0-11, 所以需要 +1
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            return `${year}/${month}/${day}`;
        } catch (error) {
            console.error("格式化日期时出错:", dateString, error);
            return "日期错误";
        }
    }

    // 创建文章卡片的函数
    function createArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'timeline-card';

        card.innerHTML = `
            <div class="card-date">${formatDate(article.published_date)}</div>
            <div class="card-content">
                <h2>${article.title}</h2>
                <p>${article.summary}</p>
                <strong>关键技巧/知识点:</strong>
                <ul>
                    ${article.skills.map(skill => `<li>${skill}</li>`).join('')}
                </ul>
                <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="read-more">阅读原文 &rarr;</a>
            </div>
        `;
        return card;
    }

    // 加载文章数据的函数
    async function loadArticles() {
        if (isLoading || allArticlesLoaded) return;
        
        isLoading = true;
        loadingIndicator.style.display = 'block';

        try {
            const skip = currentPage * articlesPerPage;
            const response = await fetch(`/api/articles?skip=${skip}&limit=${articlesPerPage}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const newArticles = await response.json();

            // --- 调试代码：将获取到的原始数据打印到控制台 ---
            console.log("从后端接收到的原始文章数据:", newArticles);
            // ------------------------------------------------

            if (newArticles.length > 0) {
                newArticles.forEach(article => {
                    const card = createArticleCard(article);
                    timeline.appendChild(card);
                });
                currentPage++;
            } else {
                // 如果返回的文章数量为0，说明所有文章都已加载
                allArticlesLoaded = true;
                loadingIndicator.innerHTML = '<p>已加载全部内容</p>';
            }
        } catch (error) {
            console.error('加载文章失败:', error);
            loadingIndicator.innerHTML = '<p>加载内容失败，请稍后重试。</p>';
        } finally {
            isLoading = false;
            // 如果不是所有文章都加载完毕，则隐藏加载指示器
            if (!allArticlesLoaded) {
                loadingIndicator.style.display = 'none';
            }
        }
    }

    // 使用 Intersection Observer 实现无限滚动
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            loadArticles();
        }
    }, {
        rootMargin: '0px',
        threshold: 1.0
    });

    // 开始观察 'load-trigger' 元素
    observer.observe(loadTrigger);

    // 初始加载第一页数据
    loadArticles();
});
