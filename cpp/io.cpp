#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>

#include "io.h"

using namespace std;

unordered_map<string, int> author_ids;
unordered_map<string, int> publication_ids;
vector<string> names;
vector<PubInfo> pub_infos;
vector<vector<pair<int, int>>> adj, citationEdges;
int V;

string remove_quotes(const string &s) {
    string ret;
    for (auto c : s) {
        if (c != '\"') {
            ret += c;
        }
    }
    return ret;
}

void read_authors(const string &path) {
    ifstream fs(path + "authors.csv");
    string line;
    getline(fs, line);
    while (getline(fs, line)) {
        string name = remove_quotes(line);
        names.push_back(name);
        author_ids[name] = V++;
    }
}

void read_publications(const string &path) {
    ifstream fs(path + "publications.csv");
    string line;
    getline(fs, line);
    while (getline(fs, line)) {
        stringstream ss(line);

        string pub_id;
        getline(ss, pub_id, ',');
        pub_id = remove_quotes(pub_id);

        string pub_year;
        getline(ss, pub_year, ',');
        pub_year = remove_quotes(pub_year);

        string title;
        getline(ss, title, ',');
        title = remove_quotes(title);

        publication_ids[pub_id] = V++;
        pub_infos.push_back(PubInfo(pub_id, stoi(pub_year), title));
    }
}

void read_edges(string path, string file_name, int edge_type) {
    ifstream fs(path + file_name);
    string line;
    getline(fs, line);

    adj.resize(V);
    while (getline(fs, line)) {
        stringstream ss(line);
        string from;
        getline(ss, from, ',');
        from = remove_quotes(from);

        int fromIdx;
        if (edge_type == CITES || edge_type == PUBLISHES) {
            fromIdx = publication_ids[from];
        } else {
            fromIdx = author_ids[from];
        }


        string to;
        getline(ss, to, ',');
        to = remove_quotes(to);
        int toIdx;
        if (edge_type == CITES) {
            toIdx = publication_ids[to];
        } else {
            toIdx = author_ids[to];
        }


        if (edge_type == CITES) {
            // in .csv file fromIdx cites toIdx
            adj[fromIdx].push_back({toIdx, CITES});
            adj[toIdx].push_back({fromIdx, SPREADS});
        } else if (edge_type == COLLABORATES) {
            adj[fromIdx].push_back({toIdx, COLLABORATES});
            adj[toIdx].push_back({fromIdx, COLLABORATES});
        } else {
            adj[fromIdx].push_back({toIdx, AUTHORED});
            adj[toIdx].push_back({fromIdx, PUBLISHES});
        }
    }
}
