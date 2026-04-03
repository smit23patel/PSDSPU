class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();

        for(int i=0; i<n; i++){
            int a = 0;
            int b = n-1;
            for(int j=i; j<n; j++){
                if(i==j) matrix[i][j] = matrix[i][j];
                else {
                    swap(matrix[i][j], matrix[j][i]);
                }
            }
            while(a<=b){
                swap(matrix[i][a], matrix[i][b]);
                a++;
                b--;
            }
           
        }
        

    }
};