import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class DataProcessor {
    private static final int THREAD_POOL_SIZE = 4;

    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        ObjectMapper objectMapper = new ObjectMapper();

        try {
            // Read JSON file
            File jsonFile = new File("data.json");
            JsonNode rootNode = objectMapper.readTree(jsonFile);

            // Submit processing tasks
            Future<JsonNode> processedData = executor.submit(() -> processData(rootNode));
            System.out.println("Processed Data: " + processedData.get());

        } catch (IOException | InterruptedException | java.util.concurrent.ExecutionException e) {
            e.printStackTrace();
        } finally {
            executor.shutdown();
        }
    }

    private static JsonNode processData(JsonNode rootNode) {
        return rootNode.findValues("data").stream()
                .filter(node -> node.get("value").asInt() > 100)
                .reduce((first, second) -> first)
                .orElse(null);
    }
}