# Candidate references (2023–2026, not yet cited)

All 15 are peer-reviewed journal articles or conference papers. On 2026-10-09 each DOI resolved on Crossref, and the authors, year, venue and pages below were taken from that record. Each paper also has a biblatex entry at the end of `references.bib`, under `% Candidates (not yet cited)`. The suggested claim is drawn from the paper's title and abstract. Read the paper before citing it for a specific number or finding.

## On-chain reputation and credit scoring

1. **`palaiokrassas2024credit`**
   Palaiokrassas, G., Scherrers, S., Makri, E., & Tassiulas, L. (2024). Machine learning in DeFi: Credit risk assessment and liquidation prediction. In *2024 IEEE International Conference on Blockchain and Cryptocurrency (ICBC)* (pp. 650–654). IEEE. https://doi.org/10.1109/ICBC59979.2024.10634435
   DOI: 10.1109/ICBC59979.2024.10634435
   Claim: wallet-level transaction features from several chains predict credit outcomes (liquidations) in DeFi lending, so on-chain behaviour carries signal that is relevant to credit.

2. **`m2026hurdle`**
   M, A., Hegde, B. R., & Das, B. (2026). Transaction graph-based predictive hurdle model for credit scoring in DeFi lending protocols. *International Journal of Data Science and Analytics, 22*(1), Article 124. https://doi.org/10.1007/s41060-026-01097-7
   DOI: 10.1007/s41060-026-01097-7
   Claim: recent work builds credit scores for DeFi lending from the structure of the transaction graph, which supports using graph position as a basis for on-chain reputation.

## Graph ranking and labelling on blockchain transaction networks

3. **`lin2024whoiswho`**
   Lin, D., Wu, J., Huang, T., Lin, K., & Zheng, Z. (2024). Who is who on Ethereum? Account labeling using heterophilic graph convolutional network. *IEEE Transactions on Systems, Man, and Cybernetics: Systems, 54*(3), 1541–1553. https://doi.org/10.1109/TSMC.2023.3329520
   DOI: 10.1109/TSMC.2023.3329520
   Claim: the role of an Ethereum account can be inferred from where it sits in the transaction graph, which motivates labelling accounts and contracts from graph structure rather than from code alone.

4. **`yan2023aparecium`**
   Yan, C., Zhang, C., Shen, M., Li, N., Liu, J., Qi, Y., Lu, Z., & Liu, Y. (2023). Aparecium: Understanding and detecting scam behaviors on Ethereum via biased random walk. *Cybersecurity, 6*(1), Article 46. https://doi.org/10.1186/s42400-023-00180-x
   DOI: 10.1186/s42400-023-00180-x
   Claim: random walks over the Ethereum interaction graph pick up scam behaviour, a recent precedent for random-walk scoring (the family PageRank belongs to) as a risk signal on chain.

5. **`mukhia2026erc20`**
   Mukhia, K., Luwang, S. R., Nurujjaman, M., Chakraborty, T., Saha, S., & Hens, C. (2026). Statistical patterns in the Ethereum blockchain: Analysis of EOAs and smart contracts in ERC20 token network. *PLOS One, 21*(10), Article e0358972. https://doi.org/10.1371/journal.pone.0358972
   DOI: 10.1371/journal.pone.0358972
   Claim: transfers in the ERC-20 network have different statistical signatures depending on whether the endpoints are EOAs or smart contracts, which supports treating contract nodes separately in a token-network ranking.

## ERC-20 approvals, approval phishing and wallet drainers

6. **`he2025drainer`**
   He, B., Hu, Y., Chen, Z., Chen, Y., Yu, T., Chang, R., Wu, L., & Zhou, Y. (2025). Unmasking the shadow economy: A deep dive into drainer-as-a-service phishing on Ethereum. In *Proceedings of the 2025 ACM Internet Measurement Conference* (pp. 430–444). ACM. https://doi.org/10.1145/3730567.3764476
   DOI: 10.1145/3730567.3764476
   Claim: wallet-drainer phishing, where victims sign transactions that let scammers withdraw their tokens, is run as an organised drainer-as-a-service business on Ethereum, which motivates risk scores for the contracts that receive approvals.

7. **`he2023txphishscope`**
   He, B., Chen, Y., Chen, Z., Hu, X., Hu, Y., Wu, L., Chang, R., Wang, H., & Zhou, Y. (2023). TxPhishScope: Towards detecting and understanding transaction-based phishing on Ethereum. In *Proceedings of the 2023 ACM SIGSAC Conference on Computer and Communications Security* (pp. 120–134). ACM. https://doi.org/10.1145/3576915.3623210
   DOI: 10.1145/3576915.3623210
   Claim: transaction-based phishing, where phishing sites trick users into signing harmful transactions, is a distinct and measurable threat on Ethereum.

8. **`chen2025payload`**
   Chen, Z., Hu, Y., He, B., Luo, D., Wu, L., & Zhou, Y. (2025). Dissecting payload-based transaction phishing on Ethereum. In *Proceedings 2025 Network and Distributed System Security Symposium*. Internet Society. https://doi.org/10.14722/ndss.2025.230311
   DOI: 10.14722/ndss.2025.230311
   Claim: phishing on Ethereum has moved from plain transfers to malicious contract-call payloads, with reported losses of more than $70 million in 2023.

9. **`adamczyk2025approval`**
   Adamczyk, B. (2025). Dissection of an approval-based trusted-token fraud scheme used across multiple blockchain systems. *IEEE Access, 13*, 34467–34482. https://doi.org/10.1109/ACCESS.2025.3543651
   DOI: 10.1109/ACCESS.2025.3543651
   Claim: approval phishing drives large, ongoing frauds across several chains and is made worse by how poorly wallets present and validate token approvals.

## Smart-contract risk and security labelling on Ethereum and L2

10. **`li2026erc20risk`**
    Li, Z., He, Z., Luo, X., Chen, T., & Zhang, X. (2026). Unveiling financially risky behaviors in Ethereum ERC20 token contracts. *Chinese Journal of Electronics, 35*(2), 668–686. https://doi.org/10.23919/cje.2025.00.156
    DOI: 10.23919/cje.2025.00.156
    Claim: ERC-20 token contracts are often customised in ways that break the standard and create financial risk for DeFi applications, which motivates contract-level risk labels.

11. **`lin2024crpwarner`**
    Lin, Z., Chen, J., Wu, J., Zhang, W., Wang, Y., & Zheng, Z. (2024). CRPWarner: Warning the risk of contract-related rug pull in DeFi smart contracts. *IEEE Transactions on Software Engineering, 50*(6), 1534–1547. https://doi.org/10.1109/TSE.2024.3392451
    DOI: 10.1109/TSE.2024.3392451
    Claim: rug-pull risk can be flagged from contract-level features, a recent precedent for assigning risk labels to individual DeFi contracts.

12. **`tang2024arbitrum`**
    Tang, X., & Shi, L. (2024). Security analysis of smart contract migration from Ethereum to Arbitrum. *Blockchains, 2*(4), 424–444. https://doi.org/10.3390/blockchains2040018
    DOI: 10.3390/blockchains2040018
    Claim: contracts on Arbitrum face risks specific to that L2 (cross-chain messaging, block properties, address aliasing and gas), so contract risk on an L2 cannot be read directly from Ethereum mainnet behaviour.

13. **`efimov2026rollup`**
    Efimov, I., Madhwal, Y., & Yanovich, Y. (2026). SoK: Cross-domain and application-layer security in Ethereum rollup ecosystems. In *2026 IEEE International Conference on Blockchain and Cryptocurrency (ICBC)* (pp. 1–14). IEEE. https://doi.org/10.1109/ICBC67748.2026.11575541
    DOI: 10.1109/ICBC67748.2026.11575541
    Claim: a recent systematisation of application-layer and cross-domain security risks in Ethereum rollups, which places contract risk on L2s in the current literature.

## Sybil detection on chain

14. **`zhou2024artemis`**
    Zhou, C., Chen, H., Wu, H., Zhang, J., & Cai, W. (2024). ARTEMIS: Detecting airdrop hunters in NFT markets with a graph learning system. In *Proceedings of the ACM Web Conference 2024* (pp. 1824–1834). ACM. https://doi.org/10.1145/3589334.3645597
    DOI: 10.1145/3589334.3645597
    Claim: graph learning on transaction networks detects Sybil-style airdrop hunters, which shows that coordinated multi-account behaviour leaves a structural trace on chain.

15. **`liu2025sybil`**
    Liu, Q., Huang, Q., Fan, F., Wu, H., & Tang, X. (2025). Detecting Sybil addresses in blockchain airdrops: A subgraph-based feature propagation and fusion approach. In *2025 IEEE International Conference on Blockchain and Cryptocurrency (ICBC)* (pp. 1–7). IEEE. https://doi.org/10.1109/ICBC64466.2025.11185061
    DOI: 10.1109/ICBC64466.2025.11185061
    Claim: features of an address's transaction subgraph separate Sybil addresses from genuine ones in airdrops, which supports the assumption that Sybil clusters can inflate graph-based scores and need to be controlled for.
