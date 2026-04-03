import java.util.HashSet;

class Solution {
    public boolean isHappy(int n) {
        HashSet<Integer> set = new HashSet<>();

        while (n != 1 && !set.contains(n)) {
            set.add(n);
            int sum = 0;

            while (n > 0) {
                int digit = n % 10;   // get last digit
                sum += digit * digit; // add square of digit
                n = n / 10;           // remove last digit
            }

            n = sum;
        }

        return n == 1;
    }
}