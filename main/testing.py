import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Fixed x-axis range
window_size = 10
x_vals = np.linspace(0, 4, window_size)

y_vals = [23, 34, 54, 34, 2, 34, 100, 45, 39, 10]

# Plot setup
fig, ax = plt.subplots()
ax.set_xlim(0, 4)
ax.set_ylim(min(y_vals), max(y_vals))
line, = ax.plot(x_vals, y_vals, 'b-', lw=2)

def get_new_y():
    return np.random.randint(0, 100)

def update(frame):
    y_vals.pop(0)                # Remove oldest y
    y_vals.append(get_new_y())   # Append new y
    line.set_ydata(y_vals)       # Only y-data changes
    return line,

ani = animation.FuncAnimation(
    fig, update,
    interval=150,
    blit=True
)

plt.title("Sliding Window Pulse Graph")
plt.xlabel("Time (static x-axis)")
plt.ylabel("Signal")
plt.grid(True)
plt.tight_layout()
plt.show()
