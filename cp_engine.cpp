#include <bits/stdc++.h>
using namespace std;

// ---------------- SEGMENT TREE ----------------
struct SegTree
{
    int n;
    vector<double> treeMin, treeMax;

    SegTree(vector<double> &a)
    {
        n = a.size();
        treeMin.assign(4 * n, 0);
        treeMax.assign(4 * n, 0);
        build(1, 0, n - 1, a);
    }

    void build(int node, int l, int r, vector<double> &a)
    {
        if (l == r)
        {
            treeMin[node] = treeMax[node] = a[l];
            return;
        }

        int mid = (l + r) / 2;
        build(2 * node, l, mid, a);
        build(2 * node + 1, mid + 1, r, a);

        treeMin[node] = min(treeMin[2 * node], treeMin[2 * node + 1]);
        treeMax[node] = max(treeMax[2 * node], treeMax[2 * node + 1]);
    }

    double getMin() { return treeMin[1]; }
    double getMax() { return treeMax[1]; }
};

// ---------------- DSU ----------------
struct DSU
{
    vector<int> parent, size;

    DSU(int n)
    {
        parent.resize(n);
        size.assign(n, 1);

        for (int i = 0; i < n; i++)
            parent[i] = i;
    }

    int find(int x)
    {
        if (parent[x] == x)
            return x;
        return parent[x] = find(parent[x]);
    }

    void unite(int a, int b)
    {
        a = find(a);
        b = find(b);

        if (a == b)
            return;

        if (size[a] < size[b])
            swap(a, b);

        parent[b] = a;
        size[a] += size[b];
    }
};

int main()
{

    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<double> price(n);

    for (int i = 0; i < n; i++)
        cin >> price[i];

    cout << fixed << setprecision(2);

    // =================================================
    // 1. STL (Set + Map) → UNIQUE_PRICES & MODE_PRICE
    // =================================================
    set<int> uniqueRounded;
    unordered_map<int, int> freq;

    for (double x : price)
    {
        int v = round(x);
        uniqueRounded.insert(v);
        freq[v]++;
    }

    // =================================================
    // 2. Prefix Sum → AVG & TOTAL_SUM
    // =================================================
    vector<double> pref(n);
    pref[0] = price[0];

    for (int i = 1; i < n; i++)
        pref[i] = pref[i - 1] + price[i];

    double totalSum = pref[n - 1];
    double avg = totalSum / n;

    // =================================================
    // 3. Difference Array → VOL_MOVEMENT
    // Measures day-to-day change
    // =================================================
    vector<double> diff(n, 0);

    for (int i = 1; i < n; i++)
        diff[i] = price[i] - price[i - 1];

    double totalMovement = 0;

    for (int i = 1; i < n; i++)
        totalMovement += abs(diff[i]);

    // =================================================
    // 4. Sliding Window → BEST_MA5
    // Moving average of size 5
    // =================================================
    int k = min(5, n);

    double window = 0;

    for (int i = 0; i < k; i++)
        window += price[i];

    double bestMA = window / k;

    for (int i = k; i < n; i++)
    {
        window += price[i];
        window -= price[i - k];
        bestMA = max(bestMA, window / k);
    }

    // =================================================
    // 5. Binary Search → BS_INDEX
    // Find where latest price sits in sorted order
    // =================================================
    vector<double> sortedP = price;
    sort(sortedP.begin(), sortedP.end());

    double target = price[n - 1];

    int idx = lower_bound(
                  sortedP.begin(),
                  sortedP.end(),
                  target) -
              sortedP.begin();

    // =================================================
    // 6. Kadane’s Algorithm → MAX_PROFIT, BUY_DAY, SELL_DAY
    // Converts prices → daily changes
    // =================================================
    double cur = 0, best = 0;
    int buy = 0, sell = 0, start = 0;

    for (int i = 1; i < n; i++)
    {
        double d = price[i] - price[i - 1];

        if (cur + d < d)
        {
            cur = d;
            start = i - 1;
        }
        else
        {
            cur += d;
        }

        if (cur > best)
        {
            best = cur;
            buy = start;
            sell = i;
        }
    }

    // =================================================
    // 7. Priority Queue → TOP1, TOP2
    // =================================================
    priority_queue<double> pq;

    for (double x : price)
        pq.push(x);

    double top1 = pq.top();
    pq.pop();
    double top2 = pq.empty() ? top1 : pq.top();

    // =================================================
    // 8. XOR / Bitmask → BIT_FLIPS
    // =================================================
    vector<int> bits;

    for (int i = 1; i < n; i++)
    {
        if (price[i] >= price[i - 1])
            bits.push_back(1);
        else
            bits.push_back(0);
    }

    int flips = 0;

    for (int i = 1; i < bits.size(); i++)
        flips += (bits[i] ^ bits[i - 1]);


    // =================================================
    // 9. DSU → DSU_CLUSTERS
    // Group adjacent similar prices (<2 diff)
    // =================================================
    DSU dsu(n);

    for (int i = 1; i < n; i++)
    {
        if (abs(price[i] - price[i - 1]) <= 2.0)
            dsu.unite(i - 1, i);
    }

    int clusters = 0;
    for (int i = 0; i < n; i++)
        if (dsu.find(i) == i)
            clusters++;

    // =================================================
    // 10. Graph Traversal → GRAPH_COMPONENTS
    // Detects no. of continuous trends
    // =================================================
    vector<vector<int>> gph(n);

    for (int i = 1; i < n - 1; i++)
    {
        if ((price[i] - price[i - 1]) * (price[i + 1] - price[i]) >= 0)
        {
            gph[i].push_back(i + 1);
            gph[i + 1].push_back(i);
        }
    }

    vector<int> vis(n, 0);

    int components = 0;

    for (int i = 0; i < n; i++)
    {
        if (!vis[i])
        {
            components++;
            queue<int> q;
            q.push(i);
            vis[i] = 1;

            while (!q.empty())
            {
                int u = q.front();
                q.pop();

                for (int v : gph[u])
                {
                    if (!vis[v])
                    {
                        vis[v] = 1;
                        q.push(v);
                    }
                }
            }
        }
    }

    // =================================================
    // 11. Segment Tree → SEG_MIN, SEG_MAX
    // Tree stores min/max efficiently
    // =================================================
    SegTree st(price);

    // =================================================
    // Most frequent rounded price
    // =================================================
    int modePrice = 0, modeFreq = 0;

    for (auto &it : freq)
    {
        if (it.second > modeFreq)
        {
            modeFreq = it.second;
            modePrice = it.first;
        }
    }

    string trend = "SIDEWAYS";
    if (price[n - 1] - price[0] > 2)
        trend = "UPTREND";
    else if (price[n - 1] - price[0] < -2)
        trend = "DOWNTREND";

    // =================================================
    // OUTPUT
    // =================================================
    cout << "AVG=" << avg << "\n";
    cout << "TOTAL_SUM=" << totalSum << "\n";
    cout << "VOL_MOVEMENT=" << totalMovement << "\n";
    cout << "BEST_MA5=" << bestMA << "\n";
    cout << "BS_INDEX=" << idx << "\n";
    cout << "MAX_PROFIT=" << best << "\n";
    cout << "BUY_DAY=" << buy + 1 << "\n";
    cout << "SELL_DAY=" << sell + 1 << "\n";
    cout << "TOP1=" << top1 << "\n";
    cout << "TOP2=" << top2 << "\n";
    cout << "BIT_FLIPS=" << flips << "\n";
    cout << "DSU_CLUSTERS=" << clusters << "\n";
    cout << "GRAPH_COMPONENTS=" << components << "\n";
    cout << "SEG_MIN=" << st.getMin() << "\n";
    cout << "SEG_MAX=" << st.getMax() << "\n";
    cout << "UNIQUE_PRICES=" << uniqueRounded.size() << "\n";
    cout << "MODE_PRICE=" << modePrice << "\n";
    cout << "TREND=" << trend << "\n";

    return 0;
}