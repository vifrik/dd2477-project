package demo;

import Math;

public class MyClass extends Something {
  private static final int CONSTANT = 5;
  int n;
  public void MyFunction(int n) { this.n = n; }
  public int getN() {
    String hello = "hello";
    Integer some_type = 38;
    int x = 3;
    int y = 2 * x;
    System.out.println(y);
    return n;
  }

  @Override
  public String toString() {
    return "some string";
  }
}
