# html_detector_lib
- 検索結果候補のCSSセレクターとそのスコアを返す

```python
import html_detector

results = html_detector.detect(html_str)
for score, selector in results:
    pass
```