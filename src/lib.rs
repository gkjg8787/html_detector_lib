use kuchiki::traits::*;
use kuchiki::NodeRef;
use pyo3::prelude::*;
use regex::Regex;
use std::collections::HashMap;

fn txt(n: &NodeRef) -> String {
    n.descendants()
        .text_nodes()
        .map(|t| t.borrow().trim().to_string())
        .filter(|s| !s.is_empty())
        .collect::<Vec<_>>()
        .join(" ")
}
fn name(n: &NodeRef) -> String {
    n.as_element()
        .map(|e| e.name.local.to_string())
        .unwrap_or_default()
}
fn class_str(n: &NodeRef) -> String {
    n.as_element()
        .and_then(|e| e.attributes.borrow().get("class").map(|s| s.to_string()))
        .unwrap_or_default()
}
fn classes(n: &NodeRef) -> Vec<String> {
    class_str(n)
        .split_whitespace()
        .map(|s| s.to_string())
        .collect()
}
fn build_selector(node: &NodeRef) -> String {
    let mut c = node.clone();
    let mut p = Vec::new();
    for _ in 0..6 {
        if c.as_document().is_some() {
            break;
        }
        if let Some(el) = c.as_element() {
            let tag = el.name.local.to_string();
            let at = el.attributes.borrow();
            if let Some(id) = at.get("id") {
                p.insert(0, format!("{}#{}", tag, id));
                break;
            }
            let cls = classes(&c);
            if cls.is_empty() {
                p.insert(0, tag)
            } else {
                p.insert(
                    0,
                    format!(
                        "{}.{}",
                        tag,
                        cls.into_iter().take(2).collect::<Vec<_>>().join(".")
                    ),
                )
            }
        }
        if let Some(pa) = c.parent() {
            c = pa
        } else {
            break;
        }
    }
    p.join(" > ")
}
fn child_elements(n: &NodeRef) -> Vec<NodeRef> {
    n.children()
        .elements()
        .map(|x| x.as_node().clone())
        .collect()
}
fn product_bits(n: &NodeRef, price: &Regex) -> (bool, bool, bool) {
    let img = n.select("img").ok().and_then(|mut x| x.next()).is_some();
    let a = n.select("a").ok().and_then(|mut x| x.next()).is_some();
    let pr = price.is_match(&txt(n));
    (img, a, pr)
}
fn product_score(n: &NodeRef, price: &Regex) -> f64 {
    let mut s = 0.0;
    let (i, a, p) = product_bits(n, price);
    if i {
        s += 3.0
    }
    if a {
        s += 2.0
    }
    if p {
        s += 5.0
    }
    let t = txt(n);
    if t.len() > 10 && t.len() < 200 {
        s += 2.0
    }
    let cls = class_str(n).to_lowercase();
    if ["product", "item", "card"].iter().any(|k| cls.contains(k)) {
        s += 3.0
    }
    s
}
fn sig(n: &NodeRef) -> String {
    let kids = child_elements(n)
        .into_iter()
        .take(5)
        .map(|k| name(&k))
        .collect::<Vec<_>>();
    format!("{}:{}", name(n), kids.join(","))
}
fn ancestors(n: &NodeRef) -> Vec<NodeRef> {
    let mut v = vec![n.clone()];
    let mut c = n.clone();
    for _ in 0..10 {
        if let Some(p) = c.parent() {
            v.push(p.clone());
            c = p
        } else {
            break;
        }
    }
    v
}
fn lca(nodes: &[NodeRef]) -> Option<NodeRef> {
    if nodes.is_empty() {
        return None;
    }
    let chains: Vec<Vec<NodeRef>> = nodes.iter().map(ancestors).collect();
    for c in &chains[0] {
        if chains.iter().all(|ch| ch.iter().any(|x| x == c)) {
            return Some(c.clone());
        }
    }
    None
}
fn smart_bonus(n: &NodeRef, price: &Regex) -> f64 {
    let kids = child_elements(n);
    if kids.len() < 3 {
        return -200.0;
    }
    let mut valid = 0usize;
    let first = name(&kids[0]);
    let mut same = true;
    for k in &kids {
        if name(k) != first {
            same = false;
        }
        let (i, a, p) = product_bits(k, price);
        if i && a && p {
            valid += 1;
        }
    }
    let ratio = valid as f64 / kids.len() as f64;
    let mut s = ratio * 220.0 + (kids.len() as f64).min(40.0);
    if same {
        s += 40.0
    } else {
        s -= 20.0;
    }
    if kids.len() > 40 {
        s -= 220.0;
    }
    let cls = class_str(n).to_lowercase();
    if ["app", "layout", "root", "wrapper", "container-fluid"]
        .iter()
        .any(|k| cls.contains(k))
    {
        s -= 180.0;
    }
    if ratio < 0.2 {
        s -= 300.0
    } else if ratio > 0.6 {
        s += 180.0;
    }
    s
}
#[pyfunction]
fn detect_fast(html_str: String) -> PyResult<Vec<(f64, String)>> {
    let doc = kuchiki::parse_html().one(html_str);
    let price = Regex::new(r"(¥|円|\$|€|税込|[0-9,]{3,})").unwrap();
    let mut cand: HashMap<usize, NodeRef> = HashMap::new();
    for css in ["img", "a"] {
        if let Ok(sel) = doc.select(css) {
            for m in sel {
                if let Some(p) = m.as_node().parent() {
                    cand.insert(&*p as *const _ as usize, p);
                }
            }
        }
    }
    for t in doc.descendants().text_nodes() {
        if price.is_match(&t.borrow()) {
            if let Some(p) = t.as_node().parent() {
                cand.insert(&*p as *const _ as usize, p);
            }
        }
    }
    let mut clusters: HashMap<String, Vec<(NodeRef, f64)>> = HashMap::new();
    for (_, n) in cand {
        let s = product_score(&n, &price);
        if s >= 5.0 {
            clusters.entry(sig(&n)).or_default().push((n, s));
        }
    }
    let mut best: HashMap<String, f64> = HashMap::new();
    for (_, items) in clusters {
        if items.len() < 3 {
            continue;
        }
        let nodes: Vec<NodeRef> = items.iter().map(|(n, _)| n.clone()).collect();
        if let Some(x) = lca(&nodes) {
            let base = nodes.len() as f64 * 5.0 + items.iter().map(|(_, s)| *s).sum::<f64>();
            let score = base + smart_bonus(&x, &price);
            let sel = build_selector(&x);
            if !sel.starts_with("html > body") {
                best.entry(sel)
                    .and_modify(|v| {
                        if score > *v {
                            *v = score
                        }
                    })
                    .or_insert(score);
            }
        }
    }
    let mut out: Vec<(f64, String)> = best.into_iter().map(|(k, v)| (v, k)).collect();
    out.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
    out.truncate(10);
    Ok(out)
}
#[pyfunction]
fn refine_xpath(html_str: String, candidates: Vec<(f64, String)>) -> PyResult<Vec<(f64, String)>> {
    let doc = kuchiki::parse_html().one(html_str);
    let price = Regex::new(r"(¥|円|\$|税込|[0-9,]{3,})").unwrap();
    let mut out = Vec::new();
    for (base, css) in candidates {
        match doc.select_first(&css) {
            Ok(m) => {
                let node = m.as_node().clone();
                let mut bonus = smart_bonus(&node, &price);
                if bonus < -100.0 {
                    for c in child_elements(&node) {
                        let b = smart_bonus(&c, &price);
                        if b > bonus {
                            bonus = b;
                        }
                    }
                }
                out.push((base + bonus, css));
            }
            Err(_) => out.push((base - 999.0, css)),
        }
    }
    out.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
    Ok(out)
}
#[pymodule]
fn _html_detector(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_fast, m)?)?;
    m.add_function(wrap_pyfunction!(refine_xpath, m)?)?;
    Ok(())
}
