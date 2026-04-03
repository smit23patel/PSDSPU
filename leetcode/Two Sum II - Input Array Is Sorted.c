class Solution {
public:
    vector<int> twoSum(vector<int>& numbers, int target) {
        vector<int>result;
        int start=0,n=numbers.size(),end=n-1;
        while(start<end)
        {
            int sum=numbers[start]+numbers[end];
            if(sum==target)
            {
                result.push_back(start+1);
                result.push_back(end+1);
                return result;
            }
            else if(sum>target) end--;
            else start++;
        }
        return{};
    }
};