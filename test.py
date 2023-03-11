from trueskill import Rating, backends, rate

p1 = Rating()
p2 = Rating()
print([round(float(x.mu) - (2 * float(x.sigma)), 2)*100 for x in [p1, p2]])
backends.choose_backend("mpmath")
updated_rating = rate(
    [[p1], [p2]],
    ranks=[0, 1]
)
print([round(float(x[0].mu) - (2 * float(x[0].sigma)), 2)*100 for x in updated_rating])