class Solution {
public:
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        int n = gas.size();
        int totalTank = 0;   // Total surplus gas
        int currTank = 0;    // Current tank starting from candidate station
        int start = 0;       // Candidate starting station

        for (int i = 0; i < n; ++i) {
            int netGas = gas[i] - cost[i];
            totalTank += netGas;
            currTank += netGas;

            // If we run out of gas, we cannot start from 'start'
            if (currTank < 0) {
                start = i + 1;  // Try next station as start
                currTank = 0;   // Reset tank
            }
        }

        return (totalTank >= 0) ? start : -1;
    }
};
