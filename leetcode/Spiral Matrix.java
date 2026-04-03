class Solution {
    public List<Integer> spiralOrder(int[][] matrix) {
        List<Integer> ans = new ArrayList<>();          

        int top = 0;                                   
        int rightColumn = matrix[0].length - 1;     
        int bottom = matrix.length - 1;            
        int leftColumn = 0;                         

        while (top <= bottom && rightColumn >= leftColumn) {
            
            for (int i = leftColumn; i <= rightColumn ; i++) {
                ans.add(matrix[top][i]);
            }
            top++;

            
            for (int i = top; i <= bottom; i++) {
                ans.add(matrix[i][rightColumn]);
            }
            rightColumn--;

            
            if(top <= bottom){
                for (int i = rightColumn; i >= leftColumn; i--) {
                    ans.add(matrix[bottom][i]);
                }
                bottom--;
            }

            
            if(leftColumn <= rightColumn){
                for (int i = bottom; i >= top; i--) {
                    ans.add(matrix[i][leftColumn]);
                }
                leftColumn++;
            }
            
        }
        return ans;
    }
}