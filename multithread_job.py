import os
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# =========================
# 1) Hàm job (ví dụ)
# =========================
def get_random_label():
    labels = ["positive", "negative", "neutral", "uncertain"]
    return {
        "label": random.choice(labels),
        "score": round(random.random(), 4),
    }

# =========================
# 2) Worker: gọi hàm + lưu file
# =========================
def run_one_request(req_id: int, out_dir: str) -> dict:
    t0 = time.time()
    result = get_random_label()
    payload = {
        "req_id": req_id,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "latency_ms": int((time.time() - t0) * 1000),
        "result": result,
    }

    path = os.path.join(out_dir, f"{req_id:06d}.json")
    tmp_path = path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)

    return payload

# =========================
# 3) Main: chạy multithread + tqdm
# =========================
if __name__ == "__main__":

    job_name = "hwsa"
    n_worker = 8
    corpus = [
        {"id": 1, "text": "Sản phẩm này dùng khá ổn so với mức giá."},
        {"id": 2, "text": "Dịch vụ chăm sóc khách hàng phản hồi rất chậm."},
        {"id": 3, "text": "Nội dung phim không mới nhưng vẫn dễ xem."},
        {"id": 4, "text": "Âm thanh to rõ, tuy nhiên hình ảnh chưa thật sắc nét."},
        {"id": 5, "text": "Tôi không chắc đây có phải là lựa chọn phù hợp hay không."},
    ]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_dir = f"{job_name}-{timestamp}"
    os.makedirs(out_dir, exist_ok=True)
    print(f"JOB: {out_dir}")

    futures = []
    ok, fail = 0, 0

    with ThreadPoolExecutor(max_workers=n_worker) as ex:
        for x in corpus:
            futures.append(ex.submit(run_one_request, x["id"], out_dir))

        for fut in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            try:
                _ = fut.result()
                ok += 1
            except Exception:
                fail += 1

    summary = {
        "job_name": job_name,
        "timestamp": timestamp,
        "num_requests": len(corpus),
        "n_worker": n_worker,
        "ok": ok,
        "fail": fail,
    }
    with open(os.path.join(out_dir, "_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("DONE:", summary)
