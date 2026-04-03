class Solution {
public:
    int hIndex(vector<int>& citations) {
    int n = citations.size();
    sort(citations.begin(), citations.end()); 
    
    int count = n;
    for(int i = 0; i < n; i++) {
        if(citations[i] >= count)
            return count;
        count--;
    }
    
    return 0;
        
    }
};