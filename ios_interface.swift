import SwiftUI

struct ContentView: View {
    @State private var age: String = ""
    @State private var position: String = ""
    @State private var hasGym: Bool = false
    @State private var equipment = Equipment()
    @State private var environment = Environment()
    @State private var showPlan: Bool = false
    @State private var weeklyPlan: [String: DayPlan] = [:]

    var body: some View {
        NavigationView {
            VStack {
                Form {
                    Section(header: Text("User Information")) {
                        TextField("Enter your age", text: $age)
                            .keyboardType(.numberPad)
                        TextField("Position (Linemen, Skill Player, Linebacker/TE)", text: $position)
                    }
                    
                    Section(header: Text("Gym & Equipment Access")) {
                        Toggle("Access to a gym nearby", isOn: $hasGym)
                        Toggle("Barbell", isOn: $equipment.barbell)
                        Toggle("Dumbbells", isOn: $equipment.dumbbells)
                        Toggle("Squat Rack", isOn: $equipment.squatRack)
                        Toggle("Sled", isOn: $equipment.sled)
                        Toggle("Resistance Bands", isOn: $equipment.resistanceBands)
                        Toggle("Pull-Up Bar", isOn: $equipment.pullUpBar)
                    }
                    
                    Section(header: Text("Environment Access")) {
                        Toggle("Grass Field", isOn: $environment.grass)
                        Toggle("Turf Field", isOn: $environment.turf)
                        Toggle("Running Track", isOn: $environment.track)
                        Toggle("Gym Floor", isOn: $environment.gymFloor)
                    }
                }
                
                Button(action: {
                    generateWeeklyPlan()
                    showPlan = true
                }) {
                    Text("Generate Weekly Plan")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding()
                
                NavigationLink(destination: PlanView(weeklyPlan: $weeklyPlan), isActive: $showPlan) {
                    EmptyView()
                }
            }
            .navigationBarTitle("Workout Tracker")
        }
    }
    
    func generateWeeklyPlan() {
        // Dummy data for demonstration
        weeklyPlan = [
            "Monday": DayPlan(focus: "Strength & Power", exercises: ["Squat", "Deadlift"]),
            "Tuesday": DayPlan(focus: "Speed & Agility", exercises: ["Sprints", "Shuttle Runs"]),
            "Wednesday": DayPlan(focus: "Recovery & Mobility", exercises: ["Foam Rolling", "Yoga"]),
            "Thursday": DayPlan(focus: "Explosiveness & Hypertrophy", exercises: ["Power Cleans", "Box Jumps"]),
            "Friday": DayPlan(focus: "Off (Active Recovery)", exercises: ["Swimming", "Bike Work"]),
            "Saturday": DayPlan(focus: "Full-Body Power", exercises: ["Trap Bar Deadlift", "Sled Push"]),
            "Sunday": DayPlan(focus: "Conditioning & Core", exercises: ["Shuttle Runs", "Planks"])
        ]
    }
}

struct Equipment {
    var barbell: Bool = false
    var dumbbells: Bool = false
    var squatRack: Bool = false
    var sled: Bool = false
    var resistanceBands: Bool = false
    var pullUpBar: Bool = false
}

struct Environment {
    var grass: Bool = false
    var turf: Bool = false
    var track: Bool = false
    var gymFloor: Bool = false
}

struct DayPlan: Identifiable {
    var id = UUID()
    var focus: String
    var exercises: [String]
}

struct PlanView: View {
    @Binding var weeklyPlan: [String: DayPlan]
    
    var body: some View {
        List {
            ForEach(weeklyPlan.keys.sorted(), id: \.self) { day in
                if let plan = weeklyPlan[day] {
                    Section(header: Text(day)) {
                        Text("Focus: \(plan.focus)")
                        ForEach(plan.exercises, id: \.self) { exercise in
                            Text(exercise)
                        }
                    }
                }
            }
        }
        .navigationBarTitle("Weekly Plan")
    }
}

@main
struct WorkoutTrackerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
