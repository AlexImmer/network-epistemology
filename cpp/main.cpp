#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <queue>
#include <map>
#include <iomanip>

#include <boost/serialization/vector.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/unordered_map.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>


#include "io.h"

//#define SRLZ_GRAPH 1
//#define SRLZ_CCS 1
//#define WEIRD_PUBS 1

const int MIN_YEAR = 1936;
const int MAX_YEAR = 2018;

using namespace std;

bool visited[MAXV];
queue<int> bfsQueue;
vector<vector<int>> components;
vector<int> compID;

bool isPublication(int idx) {
    return idx >= names.size();
}

void bfsCC(int startIdx) {
    while (!bfsQueue.empty()) {
        bfsQueue.pop();
    }
    visited[startIdx] = true;
    for (bfsQueue.push(startIdx); !bfsQueue.empty(); bfsQueue.pop()) {
        int curr = bfsQueue.front();
        components.rbegin()->push_back(curr);
        compID[curr] = components.size() - 1;
        for (auto &nxt : adj[curr]) {
            if (!visited[nxt.first]) {
                visited[nxt.first] = true;
                bfsQueue.push(nxt.first);
            }
        }
    }
}

queue<int> q;
int dist[MAXV];
void bfs(const int &year, const int &EDGE_TYPE) {
    for (; !q.empty(); q.pop()) {
        int curr = q.front();
        for (auto x : adj[curr]) {
            if (x.second != EDGE_TYPE) {
                continue;
            }
            if (EDGE_TYPE == CITES && pub_infos[x.first - names.size()].year >= year) {
                continue;
            }
            if (dist[x.first] != -1) {
                continue;
            }
            dist[x.first] = dist[curr] + 1;
            q.push(x.first);
        }
    }
}

template <typename Stream>
void reopen(Stream &ofs, const string &fileName)
{
    ofs.close();
    ofs.clear();
    ofs.open(fileName);
}

int main(int argc, char *argv[]) {
    string inPath = argv[1];
    string outPath = argv[2];
    ofstream ofs;
    ifstream ifs;

#ifdef SRLZ_GRAPH
    cerr << "Reading author file" << endl;
    read_authors(inPath);

    cerr << "Reading publication file" << endl;
    read_publications(inPath);

    cerr << "Reading coauthorship info" << endl;
    read_edges(inPath, "coauthorship.csv", COLLABORATES);

    cerr << "Reading citation data" << endl;
    read_edges(inPath, "citation.csv", CITES);

    cerr << "Reading authorship data" << endl;
    read_edges(inPath, "pub_auth.csv", PUBLISHES);

    reopen(ofs, inPath + "serialized.bak");
    boost::archive::binary_oarchive oa(ofs);
    oa << author_ids << publication_ids << names << pub_infos << adj << V;
    return 0;
#endif
    reopen(ifs, inPath + "serialized.bak");
    boost::archive::binary_iarchive ia(ifs);
    ia >> author_ids >> publication_ids >> names >> pub_infos >> adj >> V;
    cerr << "Graph successfully read" << endl;

#ifdef SRLZ_CCS
    compID.resize(V);
    for (int i = 0; i < V; i++) {
        if (!visited[i]) {
            components.push_back(vector<int>());
            bfsCC(i);
        }
    }
    reopen(ofs, inPath + "ccs.bak");
    boost::archive::binary_oarchive oarch(ofs);
    oarch << components << compID;
#endif
    reopen(ifs, inPath + "ccs.bak");
    boost::archive::binary_iarchive iaCC(ifs);
    iaCC >> components >> compID;
    cerr << "CCs successfully read" << endl;

#ifdef WEIRD_PUBS
    reopen(ofs, inPath + "weird_publications.txt");
    for (int i = 0; i < components.size(); i++) {
        vector<int> cc = components[i];
        if (cc.size() > 200) {
            continue;
        }
        for (auto v : cc) {
            if (isPublication(v)) {
                ofs << pub_infos[v - names.size()].title << endl;
            }
        }
        ofs << "---------------------------------------------------------------------------------------------" << endl << endl;
    }
#endif

/*
    // aliveness by transformation
    for (int year = MIN_YEAR; year <= MAX_YEAR; year++) {
        cerr << year << endl;
        while (!q.empty()) {
            q.pop();
        }
        memset(dist, -1, sizeof dist);
        for (int i = 0; i < pub_infos.size(); i++) {
            if (pub_infos[i].year == year) {
                dist[i + names.size()] = 0;
                q.push(i + names.size());
            }
        }
        bfs(year, CITES);
//        int min_dist = 1000;
//        int max_dist = 0;
        reopen(ofs, outPath +  "distances" + to_string(year) + ".txt");
        for (int i = 0; i < pub_infos.size(); i++) {
            int dst = dist[i + names.size()];
//            min_dist = min(min_dist, dst);
//            max_dist = max(max_dist, dst);
            ofs << dst << ",";
        }
//        cerr << min_dist << " " << max_dist << endl;
    }
*/

    // aliveness by tradition
    for (int year = MIN_YEAR; year <= MAX_YEAR; year++) {
        cerr << year << endl;
        while (!q.empty()) {
            q.pop();
        }
        memset(dist, -1, sizeof dist);
        for (int i = 0; i < pub_infos.size(); i++) {
            if (pub_infos[i].year == year) {
                for (auto x : adj[i + names.size()]) {
                    if (x.second != AUTHORED) {
                        continue;
                    }
                    dist[x.first] = 0;
                    q.push(x.first);
                }
            }
        }
        bfs(year, COLLABORATES);
        int min_dist = 1000;
        int max_dist = 0;
        reopen(ofs, outPath +  "tradition" + to_string(year) + ".txt");
        for (int i = 0; i < names.size(); i++) {
            int dst = dist[i];
            min_dist = min(min_dist, dst);
            max_dist = max(max_dist, dst);
            ofs << dst << ",";
        }
        cerr << min_dist << " " << max_dist << endl;
    }
    return 0;
}