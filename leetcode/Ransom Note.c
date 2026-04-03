class Solution {
public:
    bool canConstruct(string ransomNote, string magazine) {
        unordered_map<char,int> freqR;
        unordered_map<char,int> freqM;

        for(auto it:ransomNote){ //storing count of char in ransom
            freqR[it]++;
        }

        for(auto it : magazine){ //storing count of char in magazine
            freqM[it]++;
        }

        for(auto it : freqR){ //comparing count
            if(freqM[it.first] < it.second){
                return false;
            }
        }
        return true;

    }
};