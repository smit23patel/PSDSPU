class Solution {
public:
    bool isValidSudoku(vector<vector<char>>& board) {
       bool r[9][9] = {false};
        bool c[9][9] = {false};
        bool b[9][9] = {false};
       for(int i=0;i<9;i++){
        for(int j=0;j<9;j++){
            if(board[i][j]=='.')continue;
            int k=(i/3)*3+(j/3);
            int n=board[i][j]-'1';
            if(r[i][n]||c[j][n]||b[k][n])
            {
                return false;
                }
            r[i][n]=true;
            c[j][n]=true;
            b[k][n]=true;
        }
       }
       return true;
    }
};