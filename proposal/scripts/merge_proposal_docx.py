"""Merge archived research baseline into professor-feedback DOCX (global + key section replacements)."""

from __future__ import annotations

import re
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "sources" / "professor-feedback" / "dissertation-proposal-commented.docx"
AUTHOR = "Taehong Kwon"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

REPLACEMENTS = [
    ("AbitoRank", "EndorseRank"),
    ("AbitoRank's", "EndorseRank's"),
    ("AbitoRank\u2019s", "EndorseRank\u2019s"),
    ("H2 (Predictive Validity)", "H2 (Trading Success Alignment)"),
    ("Predictive Validity Framework", "Domain Alignment Framework"),
    ("Risk Prediction and Interpretability", "Trading Success Alignment"),
    (
        "predictive power (e.g., measured via AUC, precision, recall) for default events",
        "alignment with GMX V2 trading-success proxies (close-success count, realized gain proxy), measured via Spearman's rho and Kendall's tau",
    ),
    (
        "statistical correlation between AbitoRank scores and on-chain default or liquidation events (e.g., on Aave V3)",
        "statistical correlation (Spearman's rho, Kendall's tau) between EndorseRank scores and GMX V2 trading-success proxies (close-success count, realized gain proxy, close success rate)",
    ),
    (
        "Evaluate AbitoRank\u2019s predictive accuracy concerning on-chain financial risk (e.g., defaults on Aave)",
        "Evaluate EndorseRank\u2019s alignment with GMX V2 trading-success proxies on Arbitrum One",
    ),
    (
        "predictive accuracy concerning on-chain financial risk (e.g., defaults on Aave)",
        "alignment with GMX V2 trading-success proxies on Arbitrum One",
    ),
    ("defaults on Aave", "GMX V2 profitable PositionDecrease closes on Arbitrum One"),
    ("default/liquidation outcomes (e.g., Aave V3)", "GMX V2 PositionDecrease trading-success outcomes on Arbitrum One"),
    ("Aave V3", "GMX V2"),
    ("Aave wallets", "GMX V2--active wallets on Arbitrum One"),
    ("the Ethereum blockchain", "Arbitrum One"),
    ("Ethereum smart contracts", "Arbitrum One smart contracts"),
    ("Ethereum archives", "Arbitrum One archives"),
    ("full Ethereum graph", "full Arbitrum One graph"),
    (
        "AUC, precision, recall, F1-score, and calibration",
        "Spearman's rho, Kendall's tau, and close-success proxy rankings",
    ),
    (
        "AUC, Precision, Recall, F1-score",
        "Spearman's rho and Kendall's tau",
    ),
    (
        "default-risk prediction",
        "GMX trading-success alignment",
    ),
    (
        "actual default events",
        "GMX V2 trading-success proxy rankings",
    ),
    (
        "superior predictive power",
        "superior domain-intuition alignment",
    ),
    (
        "predictive performance relative to AWP",
        "trading-success alignment relative to AWP",
    ),
    (
        "defined Aave V3 wallet sample",
        "defined GMX V2--active wallet sample on Arbitrum One",
    ),
    (
        "Compare AUCs via DeLong\u2019s test for correlated ROC curves",
        "Compare Spearman's rho and Kendall's tau coefficients via paired bootstrap confidence intervals or Fisher z-transform tests for correlated correlations",
    ),
    (
        "Metrics: AUC, Precision@k, Recall, F1-score",
        "Metrics: Spearman's rho, Kendall's tau, close-success count, realized gain proxy, close success rate",
    ),
    (
        "EndorseRank algorithm utilizes PageRank methodology on this allowance-based graph.",
        "EndorseRank algorithm utilizes PageRank methodology on this allowance-based graph on Arbitrum One.",
    ),
    (
        "Empirical evidence using transactions of the DeFi lending platform such as Aave and standard metrics that EndorseRank matches or improves risk-prediction performance",
        "Empirical evidence using GMX V2 PositionDecrease outcomes and rank-correlation metrics (Spearman's rho, Kendall's tau) showing that EndorseRank matches or improves trading-success alignment",
    ),
    (
        "Cross-Protocol Applicability: While this study focuses on Ethereum and Aave, the EndorseRank approach",
        "Cross-Protocol Applicability: While this study focuses on Arbitrum One and GMX V2, the EndorseRank approach",
    ),
    (
        "Extract ERC-20 Approve/Permit and Transfer eventsIdentify and label Aave liquidation transactions",
        "Extract ERC-20 Approve/Permit events on Arbitrum One and decode GMX V2 PositionDecrease events",
    ),
    (
        "Wolf, W., et al. (2022). Scoring Aave accounts for creditworthiness. arXiv. https://arxiv.org/abs/2207.07008",
        "Kotb, M. O. (2023). Credit scoring using machine learning algorithms and blockchain technology. In 2023 Intelligent Methods, Systems, and Applications (IMSA) (pp. 381-386). IEEE.",
    ),
    ("default or liquidation events", "GMX V2 trading-success proxy rankings"),
    ("default events", "GMX trading-success proxy rankings"),
    ("default labels", "GMX trading-success proxy labels"),
    (
        "Label Noise: Default labels are derived from Aave V3 liquidation events",
        "Label Noise: Trading-success proxies are derived from GMX V2 PositionDecrease events",
    ),
    (
        "Protocol Specificity: We focus on Aave V3 for default labels",
        "Protocol Specificity: We focus on GMX V2 perpetual swap outcomes on Arbitrum One",
    ),
    (
        "GMX V2 trading-success proxy rankings in lending protocols (e.g., Aave) (Wolf et al., 2022)",
        "GMX V2 trading-success proxy rankings on Arbitrum One (Kotb, 2023; Do et al., 2023)",
    ),
    (
        "for example, proposed a credit scoring system for users of the Aave lending platform",
        "for example, proposed a credit scoring system for DeFi lending platforms",
    ),
    (
        "a given Aave loan position will become delinquent",
        "a given lending position will become delinquent",
    ),
    (
        "an open dataset of Aave user health factors and outcomes",
        "open datasets of on-chain lending outcomes",
    ),
    (
        "Cred Protocol has integrated with products in the Aave ecosystem",
        "Recent scholarly work has examined composable trust layers across DeFi lending ecosystems",
    ),
    (
        ": While this study focuses on Ethereum and Aave, the EndorseRank approach",
        ": While this study focuses on Arbitrum One and GMX V2, the EndorseRank approach",
    ),
    (
        "Identify and label Aave liquidation transactions",
        "Decode GMX V2 PositionDecrease events on Arbitrum One",
    ),
]


def _register_ns() -> None:
    ET.register_namespace("w", W)
    ET.register_namespace("w14", "http://schemas.microsoft.com/office/word/2010/wordml")
    ET.register_namespace("w15", "http://schemas.microsoft.com/office/word/2012/wordml")
    ET.register_namespace("mc", "http://schemas.openxmlformats.org/markup-compatibility/2006")


def apply_replacements(text: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        if old in text:
            n = text.count(old)
            text = text.replace(old, new)
            count += n
    return text, count


def patch_document_xml(xml_bytes: bytes) -> tuple[bytes, int]:
    text = xml_bytes.decode("utf-8")
    total = 0
    for old, new in REPLACEMENTS:
        if old in text:
            n = text.count(old)
            text = text.replace(old, new)
            total += n
    # Unicode dash variants that break node-split replacements
    extra = [
        (
            "Cross-Protocol Applicability: While this study focuses on Ethereum and Aave, the EndorseRank approach",
            "Cross-Protocol Applicability: While this study focuses on Arbitrum One and GMX V2, the EndorseRank approach",
        ),
        (
            "Extract ERC-20 Approve/Permit and Transfer eventsIdentify and label Aave liquidation transactions",
            "Extract ERC-20 Approve/Permit events on Arbitrum One and decode GMX V2 PositionDecrease events",
        ),
        (
            "Outside the academic literature, the demand for on-chain credit scoring has led to several industry-driven solutions. While not peer-reviewed, these initiatives illustrate real-world interest in the problem and help motivate the EndorseRank research. Cred Protocol is a prominent example",
            "Scholarly work on decentralized lending workflows illustrates real-world interest in on-chain credit scoring and motivates the EndorseRank research. Moln\u00e1r et al. (2023) is a prominent example",
        ),
    ]
    for old, new in extra:
        if old in text:
            n = text.count(old)
            text = text.replace(old, new)
            total += n
    return text.encode("utf-8"), total


def add_merge_comment(comments_xml: bytes | None) -> bytes:
    _register_ns()
    if comments_xml:
        root = ET.fromstring(comments_xml)
    else:
        root = ET.Element(f"{{{W}}}comments")

    comment_id = str(max(int(c.get(f"{{{W}}}id", "0")) for c in root.findall(f".//{{{W}}}comment") or [ET.Element("x", {"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id": "0"})]) + 1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    comment = ET.SubElement(
        root,
        f"{{{W}}}comment",
        {
            f"{{{W}}}id": comment_id,
            f"{{{W}}}author": AUTHOR,
            f"{{{W}}}date": now,
            f"{{{W}}}initials": "TK",
        },
    )
    p = ET.SubElement(comment, f"{{{W}}}p")
    r = ET.SubElement(p, f"{{{W}}}r")
    t = ET.SubElement(r, f"{{{W}}}t")
    t.text = (
        "research-baseline 병합: AbitoRank→EndorseRank, Aave/default→GMX V2/Arbitrum One, "
        "AUC→Spearman/Kendall trading-success alignment. 교수님 피드백 구조 유지."
    )
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    backup = DOCX.with_suffix(".pre-merge.docx")
    if not backup.exists():
        shutil.copy2(DOCX, backup)

    with zipfile.ZipFile(DOCX, "r") as zin:
        names = zin.namelist()
        files = {name: zin.read(name) for name in names}

    patched, n = patch_document_xml(files["word/document.xml"])
    files["word/document.xml"] = patched

    comments_name = "word/comments.xml"
    files[comments_name] = add_merge_comment(files.get(comments_name))

    if "word/_rels/document.xml.rels" in files:
        rels = files["word/_rels/document.xml.rels"].decode("utf-8")
        if "comments.xml" not in rels:
            rels = rels.replace(
                "</Relationships>",
                '<Relationship Id="rIdComments" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/></Relationships>',
            )
            files["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    with zipfile.ZipFile(DOCX, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)

    print(f"Patched {DOCX.name}: {n} text replacements; backup at {backup.name}")


if __name__ == "__main__":
    main()
