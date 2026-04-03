class Solution {
public:
    vector<string> summaryRanges(vector<int>& nums) {
        int n = nums.size();
        vector<string> res;
        if (n == 0) return res;
        int start = nums[0], prev = nums[0];
        for (int i = 1; i < n; i++) {
            if (nums[i] != prev + 1) {
                string s;
                if (start == prev) s = to_string(start);
                else s = to_string(start) + "->" + to_string(prev);
                res.push_back(s);
                start = nums[i];
            }
            prev = nums[i];
        }
        if (start == prev) res.push_back(to_string(start));
        if (start != prev) res.push_back(to_string(start) + "->" + to_string(prev));
        return res;
    }
};