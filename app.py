from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Literal
from glomark_agent import GlomarkProductScraper
from spar_agent import SparProductScraper
from cargills_agent import CargillsProductScraper
#from keells_agent import KeellsProductScraper
# import uvicorn

app = FastAPI(title="Supermarket Product Search API")


class SearchRequest(BaseModel):
    products: List[str]
    markets: List[Literal["glomark", "spar", "cargills", "keells"]] = ["glomark", "spar", "cargills", "keells"]


@app.get("/search")
def search_single_product(
    product: str = Query(..., min_length=2),
    market: Literal["glomark", "spar", "cargills", "keells", "all"] = "all"
):
    results = []

    if market in ("glomark", "all"):
        glomark = GlomarkProductScraper()
        try:
            results.append({
                "market": "glomark",
                "products": glomark.scrape_product_by_search(product)
            })
        finally:
            glomark.close()

    if market in ("spar", "all"):
        spar = SparProductScraper()
        try:
            results.append({
                "market": "spar",
                "products": spar.scrape_product_by_search(product)
            })
        finally:
            spar.close()

    if market in ("cargills", "all"):
        cargills = CargillsProductScraper()
        try:
            results.append({
                "market": "cargills",
                "products": cargills.scrape_product_by_search(product)
            })
        finally:
            cargills.close()

    # if market in ("keells", "all"):
    #     keells = KeellsProductScraper()
    #     try:
    #         results.append({
    #             "market": "keells",
    #             "products": keells.scrape_product_by_search(product)
    #         })
    #     finally:
    #         keells.close()

    return {
        "query": product,
        "results": results
    }


@app.post("/search/bulk")
def search_multiple_products(payload: SearchRequest):
    response = []

    for product in payload.products:
        item_result = {"product": product, "markets": []}

        if "glomark" in payload.markets:
            glomark = GlomarkProductScraper()
            try:
                item_result["markets"].append({
                    "market": "glomark",
                    "products": glomark.scrape_product_by_search(product)
                })
            finally:
                glomark.close()

        if "spar" in payload.markets:
            spar = SparProductScraper()
            try:
                item_result["markets"].append({
                    "market": "spar",
                    "products": spar.scrape_product_by_search(product)
                })
            finally:
                spar.close()

        if "cargills" in payload.markets:
            cargills = CargillsProductScraper()
            try:
                item_result["markets"].append({
                    "market": "cargills",
                    "products": cargills.scrape_product_by_search(product)
                })
            finally:
                cargills.close()

        # if "keells" in payload.markets:
        #     keells = KeellsProductScraper()
        #     try:
        #         item_result["markets"].append({
        #             "market": "keells",
        #             "products": keells.scrape_product_by_search(product)
        #         })
        #     finally:
        #         keells.close()

        response.append(item_result)

    return response

# ---------- Run Server ----------
# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )
